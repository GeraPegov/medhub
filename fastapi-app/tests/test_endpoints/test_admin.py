from types import SimpleNamespace

import pytest

from app.domain.exceptions import (
    AdminApiUnavailableError,
    BadGatewayError,
    NotFoundRecordsError,
)
from app.presentation.api.endpoints import admin


def mock_admin_response(status: int):
    async def request_admin_api(method: str, path: str):
        assert method == "DELETE"
        assert path == "/admin/users/1"
        return status, None

    return request_admin_api


@pytest.mark.asyncio
async def test_delete_admin_api_accepts_no_content(monkeypatch):
    monkeypatch.setattr(admin, "request_admin_api", mock_admin_response(204))

    await admin.delete_admin_api("/admin/users/1")


@pytest.mark.asyncio
async def test_delete_admin_api_returns_not_found(monkeypatch):
    monkeypatch.setattr(admin, "request_admin_api", mock_admin_response(404))

    with pytest.raises(NotFoundRecordsError):
        await admin.delete_admin_api("/admin/users/1")


@pytest.mark.asyncio
async def test_delete_admin_api_rejects_unexpected_status(monkeypatch):
    monkeypatch.setattr(admin, "request_admin_api", mock_admin_response(500))

    with pytest.raises(BadGatewayError) as error:
        await admin.delete_admin_api("/admin/users/1")

    assert error.value.status_code == 500


@pytest.mark.asyncio
async def test_get_admin_data_rejects_unexpected_status(monkeypatch):
    async def request_admin_api(method: str, path: str, **kwargs):
        return 503, None

    monkeypatch.setattr(admin, "request_admin_api", request_admin_api)

    with pytest.raises(BadGatewayError) as error:
        await admin.get_admin_data("GET", "/admin/users", {})

    assert error.value.status_code == 503


@pytest.mark.asyncio
async def test_user_delete_returns_not_found_response(monkeypatch):
    async def delete_admin_api(path: str):
        raise NotFoundRecordsError

    monkeypatch.setattr(admin, "delete_admin_api", delete_admin_api)

    response = await admin.user_delete.__wrapped__(SimpleNamespace(), user_id=1)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_check_token_returns_bad_gateway_when_admin_api_is_unavailable(
    monkeypatch,
):
    async def request_admin_api(method: str, path: str, **kwargs):
        raise AdminApiUnavailableError

    monkeypatch.setattr(admin, "request_admin_api", request_admin_api)
    request = SimpleNamespace(cookies={"admin_access_token": "token"})

    response = await admin.user_delete(request, user_id=1)

    assert response.status_code == 502
