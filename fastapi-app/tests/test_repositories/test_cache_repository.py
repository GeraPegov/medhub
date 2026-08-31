import json

import pytest
from redis.asyncio import Redis

from app.domain.entities.user import UserEntity
from app.infrastructure.database.models.user import User
from app.infrastructure.database.repositories.cache_repository import CachedRepository


@pytest.mark.asyncio
async def test_create_cash(db_redis: Redis, test_user1: User):
    repo = CachedRepository(db_redis)
    mapping = {
        "user_id": test_user1.id,
        "email": test_user1.email,
        "unique_username": test_user1.unique_username,
        "nickname": test_user1.nickname,
        "subscriptions": json.dumps(list(test_user1.subscriptions)),
    }
    key = test_user1.id

    prefix = "user"

    cache = await repo.set_cache(mapping=mapping, key=key, prefix=prefix)

    assert cache is True

    cache = await db_redis.hgetall(f"user:{test_user1.id}")

    assert int(cache["user_id"]) == test_user1.id


@pytest.mark.asyncio
async def test_cache_user(db_redis: Redis, test_cache_user_example, test_user1: User):
    repo = CachedRepository(db_redis)

    cache = await repo.get_cached_user(test_user1.id)

    assert cache.email == test_user1.email

    cache = await repo.get_cached_user(test_user1.unique_username)

    assert cache.email == test_user1.email


@pytest.mark.asyncio
async def test_delete_user(db_redis: Redis, test_cache_user_example, test_user1: User):
    repo = CachedRepository(db_redis)
    user = UserEntity(
        user_id=test_user1.id,
        email=test_user1.email,
        unique_username=test_user1.unique_username,
        nickname=test_user1.nickname,
        subscriptions=test_user1.subscriptions,
    )
    cache = await repo.delete_user(user)
    """Количество удаленных ключей"""
    assert cache == 2
