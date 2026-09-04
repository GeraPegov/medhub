import json
from unittest.mock import AsyncMock

import pytest

from app.application.services.cache_service import CachedUserService
from app.domain.entities.user import UserEntity
from app.domain.exceptions import NotFoundUserError


@pytest.fixture
def user() -> UserEntity:
    return UserEntity(
        user_id=10,
        email="any@example.com",
        unique_username="any username",
        nickname="any nickname",
        subscriptions=["any"],
    )


@pytest.fixture
def cache_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def user_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def cached_user_service(
    cache_repository: AsyncMock, user_repository: AsyncMock
) -> CachedUserService:
    return CachedUserService(cache_repository, user_repository)


@pytest.mark.asyncio
async def test_update_user_refreshes_cache(
    cached_user_service: CachedUserService,
    user: UserEntity,
    cache_repository: AsyncMock,
):
    result = await cached_user_service.update_user(user)
    data = {
        "user_id": str(user.user_id),
        "email": user.email,
        "unique_username": user.unique_username,
        "nickname": user.nickname,
        "subscriptions": json.dumps(list(user.subscriptions)),
    }

    assert result is True

    cache_repository.delete_user.assert_awaited_once_with(user)
    cache_repository.set_cache.assert_awaited_once_with(
        "user", user.user_id, data, 3600
    )


@pytest.mark.asyncio
async def test_get_user_by_id_from_cache(
    cached_user_service: CachedUserService,
    user: UserEntity,
    cache_repository: AsyncMock,
    user_repository: AsyncMock,
):
    cache_repository.get_cached_user.return_value = user

    result = await cached_user_service.get_user(user.user_id)

    assert result == user
    cache_repository.get_cached_user.assert_awaited_once_with(user.user_id)
    user_repository.get_by_id.assert_not_awaited()
    cache_repository.set_cache.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_user_by_username_from_cache(
    cached_user_service: CachedUserService,
    user: UserEntity,
    cache_repository: AsyncMock,
    user_repository: AsyncMock,
):
    cache_repository.get_cached_user.return_value = user

    result = await cached_user_service.get_user(user.unique_username)

    assert result == user
    cache_repository.get_cached_user.assert_awaited_once_with(user.unique_username)
    user_repository.get_by_username.assert_not_awaited()
    cache_repository.set_cache.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_user_by_id_from_user_repository(
    cached_user_service: CachedUserService,
    user: UserEntity,
    cache_repository: AsyncMock,
    user_repository: AsyncMock,
):
    cache_repository.get_cached_user.return_value = None
    user_repository.get_by_id.return_value = user
    result = await cached_user_service.get_user(user.user_id)
    assert result == user

    data = {
        "user_id": user.user_id,
        "email": user.email,
        "unique_username": user.unique_username,
        "nickname": user.nickname,
        "subscriptions": json.dumps(list(user.subscriptions)),
    }

    cache_repository.get_cached_user.assert_awaited_once_with(user.user_id)
    user_repository.get_by_id.assert_awaited_once_with(user.user_id)
    cache_repository.set_cache.assert_awaited_once_with(
        "user", user.user_id, data, 3600
    )


@pytest.mark.asyncio
async def test_get_user_by_username_from_user_repository(
    cached_user_service: CachedUserService,
    user: UserEntity,
    cache_repository: AsyncMock,
    user_repository: AsyncMock,
):
    cache_repository.get_cached_user.return_value = None
    user_repository.get_by_username.return_value = user
    result = await cached_user_service.get_user(user.unique_username)
    assert result == user

    data = {
        "user_id": user.user_id,
        "email": user.email,
        "unique_username": user.unique_username,
        "nickname": user.nickname,
        "subscriptions": json.dumps(list(user.subscriptions)),
    }

    cache_repository.get_cached_user.assert_awaited_once_with(user.unique_username)
    user_repository.get_by_username.assert_awaited_once_with(user.unique_username)
    cache_repository.set_cache.assert_awaited_once_with(
        "user", user.unique_username, data, 3600
    )


@pytest.mark.asyncio
async def test_get_user_by_id_raises_when_user_not_found(
    cached_user_service: CachedUserService,
    user: UserEntity,
    cache_repository: AsyncMock,
    user_repository: AsyncMock,
):
    cache_repository.get_cached_user.return_value = None
    user_repository.get_by_id.return_value = None

    with pytest.raises(NotFoundUserError):
        await cached_user_service.get_user(user.user_id)

    cache_repository.get_cached_user.assert_awaited_once_with(user.user_id)
    user_repository.get_by_id.assert_awaited_once_with(user.user_id)
    cache_repository.set_cache.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_user_by_username_raises_when_user_not_found(
    cached_user_service: CachedUserService,
    user: UserEntity,
    cache_repository: AsyncMock,
    user_repository: AsyncMock,
):
    cache_repository.get_cached_user.return_value = None
    user_repository.get_by_username.return_value = None

    with pytest.raises(NotFoundUserError):
        await cached_user_service.get_user(user.unique_username)

    cache_repository.get_cached_user.assert_awaited_once_with(user.unique_username)
    user_repository.get_by_username.assert_awaited_once_with(user.unique_username)
    cache_repository.set_cache.assert_not_awaited()
