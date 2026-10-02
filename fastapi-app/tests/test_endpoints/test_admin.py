import re
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from starlette.middleware.sessions import SessionMiddleware

from app.application.services.cache_service import (
    CachedArticleService,
    CachedCommentService,
    CachedUserService,
)
from app.application.services.comment_service import CommentService
from app.domain.entities.user import UserEntity
from app.domain.exceptions import (
    AdminApiUnavailableError,
    BadGatewayError,
    NotFoundRecordsError,
)
from app.presentation.api.endpoints import admin


def mock_admin_response(status: int):
    async def request_admin_api(
        method: str,
        path: str,
        headers_data: dict[str, str],
    ):
        assert method == "DELETE"
        assert path == "/admin/users/1"
        assert headers_data == {"Authorization": "Bearer token"}
        return status, None

    return request_admin_api


@pytest.mark.asyncio
async def test_delete_admin_api_accepts_no_content(monkeypatch):
    monkeypatch.setattr(admin, "request_admin_api", mock_admin_response(204))

    await admin.delete_admin_api(
        "/admin/users/1",
        {"Authorization": "Bearer token"},
    )


@pytest.mark.asyncio
async def test_delete_admin_api_returns_not_found(monkeypatch):
    monkeypatch.setattr(admin, "request_admin_api", mock_admin_response(404))

    with pytest.raises(NotFoundRecordsError):
        await admin.delete_admin_api(
            "/admin/users/1",
            {"Authorization": "Bearer token"},
        )


@pytest.mark.asyncio
async def test_delete_admin_api_rejects_unexpected_status(monkeypatch):
    monkeypatch.setattr(admin, "request_admin_api", mock_admin_response(500))

    with pytest.raises(BadGatewayError) as error:
        await admin.delete_admin_api(
            "/admin/users/1",
            {"Authorization": "Bearer token"},
        )

    assert error.value.status_code == 500


@pytest.mark.asyncio
async def test_get_admin_data_rejects_unexpected_status(monkeypatch):
    async def request_admin_api(method: str, path: str, **kwargs):
        return 503, None

    monkeypatch.setattr(admin, "request_admin_api", request_admin_api)

    with pytest.raises(BadGatewayError) as error:
        await admin.get_admin_data(
            "GET",
            "/admin/users",
            {},
            {"Authorization": "Bearer token"},
        )

    assert error.value.status_code == 503


@pytest.mark.asyncio
async def test_user_delete_returns_not_found_response(monkeypatch):
    async def delete_admin_api(path: str, headers: dict[str, str]):
        assert path == "/admin/users/1"
        assert headers == {"Authorization": "Bearer token"}
        raise NotFoundRecordsError

    monkeypatch.setattr(admin, "delete_admin_api", delete_admin_api)
    request = SimpleNamespace(
        cookies={"admin_access_token": "token"}, session={"csrf_token": "valid"}
    )
    cached_user_service = AsyncMock(spec=CachedUserService)
    cached_user_service.get_user.return_value = UserEntity(
        user_id=1,
        email="user@example.com",
        unique_username="user",
        nickname="User",
        subscriptions=[],
    )

    response = await admin.user_delete(
        request,
        user_id=1,
        csrf_token="valid",
        cached_user_service=cached_user_service,
    )

    assert response.status_code == 404
    cached_user_service.invalidate_user.assert_not_awaited()


@pytest.mark.asyncio
async def test_check_token_returns_bad_gateway_when_admin_api_is_unavailable(
    monkeypatch,
):
    async def request_admin_api(method: str, path: str, **kwargs):
        raise AdminApiUnavailableError

    monkeypatch.setattr(admin, "request_admin_api", request_admin_api)
    request = SimpleNamespace(
        cookies={"admin_access_token": "token"}, session={"csrf_token": "valid"}
    )
    cached_user_service = AsyncMock(spec=CachedUserService)
    cached_user_service.get_user.return_value = UserEntity(
        user_id=1,
        email="user@example.com",
        unique_username="user",
        nickname="User",
        subscriptions=[],
    )

    response = await admin.user_delete(
        request,
        user_id=1,
        csrf_token="valid",
        cached_user_service=cached_user_service,
    )

    assert response.status_code == 502
    cached_user_service.invalidate_user.assert_not_awaited()


@pytest.mark.asyncio
async def test_admin_user_delete_invalidates_cache_without_second_database_delete(
    monkeypatch,
):
    delete_admin_api = AsyncMock()
    monkeypatch.setattr(admin, "delete_admin_api", delete_admin_api)
    request = SimpleNamespace(
        cookies={"admin_access_token": "token"}, session={"csrf_token": "valid"}
    )
    user = UserEntity(
        user_id=1,
        email="user@example.com",
        unique_username="user",
        nickname="User",
        subscriptions=[],
    )
    cached_user_service = AsyncMock(spec=CachedUserService)
    cached_user_service.get_user.return_value = user

    response = await admin.user_delete(
        request,
        user_id=1,
        csrf_token="valid",
        cached_user_service=cached_user_service,
    )

    assert response.status_code == 303
    delete_admin_api.assert_awaited_once_with(
        "/admin/users/1", {"Authorization": "Bearer token"}
    )
    cached_user_service.invalidate_user.assert_awaited_once_with(user)
    cached_user_service.delete_user.assert_not_awaited()


@pytest.mark.asyncio
async def test_admin_article_delete_invalidates_article_and_comments_cache(
    monkeypatch,
):
    delete_admin_api = AsyncMock()
    monkeypatch.setattr(admin, "delete_admin_api", delete_admin_api)
    request = SimpleNamespace(
        cookies={"admin_access_token": "token"}, session={"csrf_token": "valid"}
    )
    cached_article_service = AsyncMock(spec=CachedArticleService)

    response = await admin.article_delete(
        request,
        article_id=7,
        csrf_token="valid",
        cached_article_service=cached_article_service,
    )

    assert response.status_code == 303
    delete_admin_api.assert_awaited_once_with(
        "/admin/articles/7", {"Authorization": "Bearer token"}
    )
    cached_article_service.invalidate_article.assert_awaited_once_with(7)
    cached_article_service.delete_article.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("path", "form_data"),
    [
        ("/admin/login", {"login": "admin", "password": "secret"}),
        ("/admin/users/1", {}),
        ("/admin/articles/1", {}),
        ("/admin/comments/1", {}),
    ],
)
async def test_admin_post_rejects_invalid_csrf_without_calling_admin_api(
    monkeypatch, path: str, form_data: dict[str, str]
):
    delete_admin_api = AsyncMock()
    cached_article_service = AsyncMock(spec=CachedArticleService)
    cached_comment_service = AsyncMock(spec=CachedCommentService)
    cached_user_service = AsyncMock(spec=CachedUserService)
    comment_service = AsyncMock(spec=CommentService)
    monkeypatch.setattr(admin, "delete_admin_api", delete_admin_api)
    client_session = Mock()
    monkeypatch.setattr(admin.aiohttp, "ClientSession", client_session)

    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key="test-session-secret")
    app.include_router(admin.router)
    app.dependency_overrides[admin.get_cached_article_service] = lambda: (
        cached_article_service
    )
    app.dependency_overrides[admin.get_cached_user_service] = lambda: (
        cached_user_service
    )
    app.dependency_overrides[admin.get_cached_comment_service] = lambda: (
        cached_comment_service
    )
    app.dependency_overrides[admin.get_comment_service] = lambda: comment_service

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        await client.get("/admin/login")
        response = await client.post(path, data={**form_data, "csrf_token": "invalid"})

    assert response.status_code == 403
    assert "Невалидный CSRF-токен" in response.text
    delete_admin_api.assert_not_awaited()
    cached_article_service.invalidate_article.assert_not_awaited()
    cached_comment_service.invalidate_comments.assert_not_awaited()
    cached_user_service.invalidate_user.assert_not_awaited()
    client_session.assert_not_called()


@pytest.mark.asyncio
async def test_comment_delete_form_sends_csrf_token(monkeypatch):
    async def get_admin_data(method: str, path: str, params: dict, headers: dict):
        assert method == "GET"
        assert path == "/admin/comments"
        return [
            {
                "comment_id": 19,
                "content": "Test comment",
                "created_at": "2026-09-18T12:00:00",
            }
        ]

    delete_admin_api = AsyncMock()
    comment_service = AsyncMock(spec=CommentService)
    cached_comment_service = AsyncMock(spec=CachedCommentService)
    comment_service.get_article_id.return_value = 7
    monkeypatch.setattr(admin, "get_admin_data", get_admin_data)
    monkeypatch.setattr(admin, "delete_admin_api", delete_admin_api)

    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key="test-session-secret")
    app.include_router(admin.router)
    app.dependency_overrides[admin.get_comment_service] = lambda: comment_service
    app.dependency_overrides[admin.get_cached_comment_service] = lambda: (
        cached_comment_service
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        client.cookies.set("admin_access_token", "admin-token")
        page = await client.get("/admin/comments")
        token_input = re.search(r'name="csrf_token" value="([^"]+)"', page.text)
        assert page.status_code == 200
        assert token_input is not None

        response = await client.post(
            "/admin/comments/19", data={"csrf_token": token_input.group(1)}
        )

    assert response.status_code == 303
    delete_admin_api.assert_awaited_once_with(
        "/admin/comments/19", {"Authorization": "Bearer admin-token"}
    )
    comment_service.get_article_id.assert_awaited_once_with(19)
    cached_comment_service.invalidate_comments.assert_awaited_once_with(7)


@pytest.mark.asyncio
async def test_articles_page_forwards_date_and_links_to_article(monkeypatch):
    async def get_admin_data(method: str, path: str, params: dict, headers: dict):
        assert method == "GET"
        assert path == "/admin/articles"
        assert params == {"public_date": "2026-09-27"}
        assert headers == {"Authorization": "Bearer admin-token"}
        return [
            {
                "article_id": 19,
                "user_id": 7,
                "title": "Test article",
                "created_at": "2026-09-27T12:00:00",
            }
        ]

    monkeypatch.setattr(admin, "get_admin_data", get_admin_data)

    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key="test-session-secret")
    app.include_router(admin.router)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        client.cookies.set("admin_access_token", "admin-token")
        response = await client.get(
            "/admin/articles", params={"public_date": "2026-09-27"}
        )

    assert response.status_code == 200
    assert 'href="/article/19"' in response.text
    assert response.text.count('action="/admin/articles" method="get"') == 1
    assert 'name="public_date"' in response.text
    assert 'type="date"' in response.text
    assert 'value="2026-09-27"' in response.text
