import re
from dataclasses import replace
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from starlette.middleware.sessions import SessionMiddleware

from app.application.services.article_service import ArticleService
from app.application.services.cache_service import CachedArticleService
from app.application.services.comment_service import CommentService
from app.domain.entities.article import ArticleEntity
from app.domain.entities.user import UserEntity
from app.domain.exceptions import NotFoundArticleError, ReactionAlreadyExistsError
from app.presentation.api.endpoints import articles
from app.presentation.dependencies.articles_dependencies import get_article_service
from app.presentation.dependencies.cache import get_cached_article_service
from app.presentation.dependencies.comments import get_comment_service
from app.presentation.dependencies.current_user import get_current_user


@pytest.fixture
def article() -> ArticleEntity:
    return ArticleEntity(
        article_id=7,
        title="Evidence based medicine",
        content="A sufficiently detailed article body.",
        user_id=42,
        category="Research",
        unique_username="author",
        nickname="Author",
        likes=3,
        dislikes=1,
        created_at=datetime(2026, 8, 31, 12, 0),
    )


@pytest.fixture
def current_user() -> UserEntity:
    return UserEntity(
        user_id=42,
        email="author@example.com",
        unique_username="author",
        nickname="Author",
        subscriptions=[],
    )


@pytest.fixture
def article_service() -> AsyncMock:
    return AsyncMock(spec=ArticleService)


@pytest.fixture
def cached_article_service() -> AsyncMock:
    return AsyncMock(spec=CachedArticleService)


@pytest.fixture
def comment_service() -> AsyncMock:
    return AsyncMock(spec=CommentService)


@pytest.fixture
async def article_client(
    current_user: UserEntity,
    article_service: AsyncMock,
    cached_article_service: AsyncMock,
    comment_service: AsyncMock,
):
    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key="test-session-secret")
    app.include_router(articles.router)
    auth_state = {"user": current_user}

    async def override_current_user():
        return auth_state["user"]

    app.dependency_overrides[get_current_user] = override_current_user
    app.dependency_overrides[get_article_service] = lambda: article_service
    app.dependency_overrides[get_cached_article_service] = lambda: (
        cached_article_service
    )
    app.dependency_overrides[get_comment_service] = lambda: comment_service

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        follow_redirects=False,
    ) as client:
        yield client, auth_state


async def get_csrf_token(client: AsyncClient) -> str:
    response = await client.get("/article/submit")
    assert response.status_code == 200
    match = re.search(r'name="csrf_token"\s+value="([^"]+)"', response.text)
    assert match is not None
    return match.group(1)


def valid_article_form(csrf_token: str) -> dict[str, str]:
    return {
        "csrf_token": csrf_token,
        "title": "Updated article",
        "content": "A sufficiently detailed updated body.",
        "category": "Research",
    }


@pytest.mark.asyncio
async def test_show_article_renders_article_and_updates_view_counter(
    article_client,
    article: ArticleEntity,
    cached_article_service: AsyncMock,
    comment_service: AsyncMock,
):
    client, _ = article_client
    cached_article_service.get_article.return_value = article
    comment_service.list_by_article_id.return_value = None

    response = await client.get(f"/article/{article.article_id}")

    assert response.status_code == 200
    assert article.title in response.text
    assert article.content in response.text
    cached_article_service.get_article.assert_awaited_once_with(article.article_id)
    cached_article_service.increment_view_counter.assert_awaited_once_with(
        article.article_id
    )
    comment_service.list_by_article_id.assert_awaited_once_with(article.article_id)


@pytest.mark.asyncio
async def test_show_article_returns_404_without_side_effects_when_missing(
    article_client,
    cached_article_service: AsyncMock,
    comment_service: AsyncMock,
):
    client, _ = article_client
    cached_article_service.get_article.side_effect = NotFoundArticleError

    response = await client.get("/article/999999")

    assert response.status_code == 404
    assert "Статья не найдена" in response.text
    cached_article_service.increment_view_counter.assert_not_awaited()
    comment_service.list_by_article_id.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_article_deletes_database_and_cache_for_authenticated_owner(
    article_client,
    article: ArticleEntity,
    current_user: UserEntity,
    article_service: AsyncMock,
    cached_article_service: AsyncMock,
):
    client, _ = article_client
    token = await get_csrf_token(client)

    response = await client.post(
        f"/article/delete/{article.article_id}", data={"csrf_token": token}
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/user/profile/author"
    article_service.delete_article.assert_awaited_once_with(
        article.article_id, current_user.user_id
    )
    cached_article_service.delete_article.assert_awaited_once_with(article.article_id)


@pytest.mark.asyncio
async def test_delete_article_redirects_anonymous_user_without_deleting(
    article_client,
    article: ArticleEntity,
    article_service: AsyncMock,
    cached_article_service: AsyncMock,
):
    client, auth_state = article_client
    auth_state["user"] = None

    response = await client.post(
        f"/article/delete/{article.article_id}", data={"csrf_token": "unused"}
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/auth"
    article_service.delete_article.assert_not_awaited()
    cached_article_service.delete_article.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_article_rejects_invalid_csrf_before_deleting(
    article_client,
    article: ArticleEntity,
    article_service: AsyncMock,
    cached_article_service: AsyncMock,
):
    client, _ = article_client

    response = await client.post(
        f"/article/delete/{article.article_id}", data={"csrf_token": "invalid"}
    )

    assert response.status_code == 403
    assert "Невалидный CSRF-токен" in response.text
    article_service.delete_article.assert_not_awaited()
    cached_article_service.delete_article.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_article_returns_404_and_preserves_cache_when_database_misses(
    article_client,
    article: ArticleEntity,
    article_service: AsyncMock,
    cached_article_service: AsyncMock,
):
    client, _ = article_client
    token = await get_csrf_token(client)
    article_service.delete_article.side_effect = NotFoundArticleError

    response = await client.post(
        f"/article/delete/{article.article_id}", data={"csrf_token": token}
    )

    assert response.status_code == 404
    cached_article_service.delete_article.assert_not_awaited()


@pytest.mark.asyncio
async def test_change_page_is_available_only_to_article_owner(
    article_client,
    article: ArticleEntity,
    article_service: AsyncMock,
):
    client, _ = article_client
    article_service.get_by_id.return_value = article

    response = await client.get(f"/article/change/{article.article_id}")

    assert response.status_code == 200
    assert article.title in response.text
    article_service.get_by_id.assert_awaited_once_with(article.article_id)


@pytest.mark.asyncio
async def test_change_page_rejects_non_owner(
    article_client,
    article: ArticleEntity,
    article_service: AsyncMock,
):
    client, _ = article_client
    article_service.get_by_id.return_value = replace(article, user_id=999)

    response = await client.get(f"/article/change/{article.article_id}")

    assert response.status_code == 403
    assert "Недостаточно прав" in response.text


@pytest.mark.asyncio
async def test_change_page_redirects_anonymous_user_without_querying_article(
    article_client,
    article: ArticleEntity,
    article_service: AsyncMock,
):
    client, auth_state = article_client
    auth_state["user"] = None

    response = await client.get(f"/article/change/{article.article_id}")

    assert response.status_code == 303
    assert response.headers["location"] == "/auth"
    article_service.get_by_id.assert_not_awaited()


@pytest.mark.asyncio
async def test_change_page_returns_404_for_missing_article(
    article_client,
    article: ArticleEntity,
    article_service: AsyncMock,
):
    client, _ = article_client
    article_service.get_by_id.side_effect = NotFoundArticleError

    response = await client.get(f"/article/change/{article.article_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_final_change_updates_article_and_cache(
    article_client,
    article: ArticleEntity,
    current_user: UserEntity,
    article_service: AsyncMock,
    cached_article_service: AsyncMock,
):
    client, _ = article_client
    token = await get_csrf_token(client)
    updated = replace(article, title="Updated article")
    article_service.change_article.return_value = updated

    response = await client.post(
        f"/article/change/{article.article_id}/access",
        data=valid_article_form(token),
    )

    assert response.status_code == 303
    assert response.headers["location"] == f"/article/{article.article_id}"
    dto, article_id, user_id = article_service.change_article.await_args.args
    assert dto.title == "Updated article"
    assert dto.content == "A sufficiently detailed updated body."
    assert dto.category == "Research"
    assert article_id == article.article_id
    assert user_id == current_user.user_id
    cached_article_service.update_article.assert_awaited_once_with(updated)


@pytest.mark.asyncio
async def test_final_change_does_not_touch_cache_when_article_is_missing(
    article_client,
    article: ArticleEntity,
    article_service: AsyncMock,
    cached_article_service: AsyncMock,
):
    client, _ = article_client
    token = await get_csrf_token(client)
    article_service.change_article.side_effect = NotFoundArticleError

    response = await client.post(
        f"/article/change/{article.article_id}/access",
        data=valid_article_form(token),
    )

    assert response.status_code == 404
    cached_article_service.update_article.assert_not_awaited()


@pytest.mark.asyncio
async def test_reaction_returns_updated_counters(
    article_client,
    article: ArticleEntity,
    current_user: UserEntity,
    cached_article_service: AsyncMock,
):
    client, _ = article_client
    token = await get_csrf_token(client)
    cached_article_service.add_reaction.return_value = {"likes": 4, "dislikes": 1}

    response = await client.post(
        f"/article/like/{article.article_id}", headers={"X-CSRF-Token": token}
    )

    assert response.status_code == 200
    assert response.json() == {"likes": 4, "dislikes": 1}
    cached_article_service.add_reaction.assert_awaited_once_with(
        article_id=article.article_id,
        user_id=current_user.user_id,
        reaction="like",
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("error", "status_code", "message"),
    [
        (NotFoundArticleError, 404, "Статья не найдена"),
        (ReactionAlreadyExistsError, 409, "Вы уже поставили реакцию"),
    ],
)
async def test_reaction_maps_domain_errors_to_http_responses(
    article_client,
    article: ArticleEntity,
    cached_article_service: AsyncMock,
    error: type[Exception],
    status_code: int,
    message: str,
):
    client, _ = article_client
    token = await get_csrf_token(client)
    cached_article_service.add_reaction.side_effect = error

    response = await client.post(
        f"/article/like/{article.article_id}", headers={"X-CSRF-Token": token}
    )

    assert response.status_code == status_code
    assert message in response.json()["error"]


@pytest.mark.asyncio
async def test_reaction_requires_authentication(
    article_client,
    article: ArticleEntity,
    cached_article_service: AsyncMock,
):
    client, auth_state = article_client
    auth_state["user"] = None

    response = await client.post(
        f"/article/like/{article.article_id}", headers={"X-CSRF-Token": "unused"}
    )

    assert response.status_code == 401
    cached_article_service.add_reaction.assert_not_awaited()


@pytest.mark.asyncio
async def test_reaction_rejects_invalid_csrf(
    article_client,
    article: ArticleEntity,
    cached_article_service: AsyncMock,
):
    client, _ = article_client

    response = await client.post(
        f"/article/dislike/{article.article_id}",
        headers={"X-CSRF-Token": "invalid"},
    )

    assert response.status_code == 403
    cached_article_service.add_reaction.assert_not_awaited()


@pytest.mark.asyncio
async def test_reaction_rejects_unknown_reaction_value(article_client):
    client, _ = article_client

    response = await client.post("/article/love/7", headers={"X-CSRF-Token": "unused"})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_search_by_title_delegates_query_and_renders_results(
    article_client,
    article: ArticleEntity,
    article_service: AsyncMock,
):
    client, _ = article_client
    article_service.search_by_title.return_value = [article]

    response = await client.get("/articles/search/title", params={"query": "evidence"})

    assert response.status_code == 200
    assert article.title in response.text
    article_service.search_by_title.assert_awaited_once_with("evidence")


@pytest.mark.asyncio
async def test_search_by_title_validates_minimum_query_length(
    article_client, article_service: AsyncMock
):
    client, _ = article_client

    response = await client.get("/articles/search/title", params={"query": "x"})

    assert response.status_code == 422
    article_service.search_by_title.assert_not_awaited()


@pytest.mark.asyncio
async def test_search_by_category_delegates_category_and_renders_results(
    article_client,
    article: ArticleEntity,
    article_service: AsyncMock,
):
    client, _ = article_client
    article_service.search_by_category.return_value = [article]

    response = await client.get("/articles/search/category/Research")

    assert response.status_code == 200
    assert article.title in response.text
    article_service.search_by_category.assert_awaited_once_with("Research")


@pytest.mark.asyncio
async def test_submit_page_redirects_anonymous_user(article_client):
    client, auth_state = article_client
    auth_state["user"] = None

    response = await client.get("/article/submit")

    assert response.status_code == 303
    assert response.headers["location"] == "/auth"


@pytest.mark.asyncio
async def test_create_article_submits_valid_dto_and_redirects_to_profile(
    article_client,
    article: ArticleEntity,
    current_user: UserEntity,
    article_service: AsyncMock,
):
    client, _ = article_client
    token = await get_csrf_token(client)
    article_service.submit_article.return_value = article

    response = await client.post("/article/submit/add", data=valid_article_form(token))

    assert response.status_code == 303
    assert response.headers["location"] == "/user/profile/author"
    dto, user_id = article_service.submit_article.await_args.args
    assert dto.title == "Updated article"
    assert dto.content == "A sufficiently detailed updated body."
    assert dto.category == "Research"
    assert user_id == current_user.user_id


@pytest.mark.asyncio
async def test_create_article_returns_429_when_daily_limit_is_reached(
    article_client, article_service: AsyncMock
):
    client, _ = article_client
    token = await get_csrf_token(client)
    article_service.submit_article.return_value = None

    response = await client.post("/article/submit/add", data=valid_article_form(token))

    assert response.status_code == 429
    assert "Достигнут дневной лимит" in response.text


@pytest.mark.asyncio
async def test_create_article_rejects_invalid_csrf_before_service_call(
    article_client, article_service: AsyncMock
):
    client, _ = article_client

    response = await client.post(
        "/article/submit/add", data=valid_article_form("invalid")
    )

    assert response.status_code == 403
    article_service.submit_article.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_article_rejects_invalid_dto_before_service_call(
    article_client, article_service: AsyncMock
):
    client, _ = article_client
    token = await get_csrf_token(client)
    invalid_form = valid_article_form(token)
    invalid_form["title"] = "x"

    response = await client.post("/article/submit/add", data=invalid_form)

    assert response.status_code == 422
    article_service.submit_article.assert_not_awaited()
