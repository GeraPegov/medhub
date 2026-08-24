import pytest
from fastapi import HTTPException

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

    with pytest.raises(HTTPException) as error:
        await admin.delete_admin_api("/admin/users/1")

    assert error.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_admin_api_rejects_unexpected_status(monkeypatch):
    monkeypatch.setattr(admin, "request_admin_api", mock_admin_response(500))

    with pytest.raises(HTTPException) as error:
        await admin.delete_admin_api("/admin/users/1")

    assert error.value.status_code == 502
