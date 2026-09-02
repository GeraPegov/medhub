from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI, Request
from httpx import ASGITransport, AsyncClient
from starlette.middleware.sessions import SessionMiddleware

from app.application.services.comment_service import CommentService
from app.domain.entities.user import UserEntity
from app.domain.exceptions import NotFoundArticleError, NotFoundUserError
from app.presentation.api.endpoints import comments
from app.presentation.dependencies.comments import get_comment_service
from app.presentation.dependencies.current_user import get_current_user


@pytest.fixture
def comment_service() -> AsyncMock:
    return AsyncMock(spec=CommentService)


@pytest.fixture
async def comment_client(comment_service: AsyncMock):
    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key="test-session-secret")
    app.include_router(comments.router)
    user = UserEntity(
        user_id=42,
        email="author@example.com",
        unique_username="author",
        nickname="Author",
        subscriptions=[],
    )
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_comment_service] = lambda: comment_service

    @app.get("/test/csrf")
    async def csrf_token(request: Request):
        request.session["csrf_token"] = "test-csrf-token"
        return {"csrf_token": request.session["csrf_token"]}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        token = (await client.get("/test/csrf")).json()["csrf_token"]
        yield client, token


@pytest.mark.asyncio
@pytest.mark.parametrize("error", [NotFoundUserError, NotFoundArticleError])
async def test_create_returns_404_when_user_or_article_is_missing(
    comment_client, comment_service: AsyncMock, error: type[Exception]
):
    client, token = comment_client
    comment_service.create.side_effect = error

    response = await client.post(
        "/comments/7/create",
        data={"content": "Test comment", "csrf_token": token},
    )

    assert response.status_code == 404
    assert response.json() == {"error": "Не существует пользователя или статьи"}
    comment_service.create.assert_awaited_once_with(
        article_id=7, content="Test comment", user_id=42
    )


@pytest.mark.asyncio
async def test_delete_redirects_to_article_returned_by_service(
    comment_client, comment_service: AsyncMock
):
    client, token = comment_client
    comment_service.delete.return_value = 7

    response = await client.post("/comments/13/delete", data={"csrf_token": token})

    assert response.status_code == 303
    assert response.headers["location"] == "/article/7"
    comment_service.delete.assert_awaited_once_with(comment_id=13, user_id=42)
