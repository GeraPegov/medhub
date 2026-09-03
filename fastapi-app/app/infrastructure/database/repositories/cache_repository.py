import json
from collections.abc import Awaitable, Callable
from datetime import datetime
from functools import wraps
from typing import Any, ParamSpec, TypeVar, cast

from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

from app.domain.entities.article import ArticleEntity
from app.domain.entities.user import UserEntity
from app.domain.logging import logger

P = ParamSpec("P")
T = TypeVar("T")


def handle_redis_errors(default_return: Any = None):
    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T | Any]]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except (RedisConnectionError, RedisTimeoutError) as e:
                logger.warning(f"Redis error in {func.__name__}: {e}")
                return default_return

        return wrapper

    return decorator


class CachedRepository:
    def __init__(self, connection: Redis):
        self.connection = connection


    @handle_redis_errors(default_return=None)
    async def increment_view_counter(self, article_id: int):
        return await self.connection.incr(f"article_counter:{article_id}")


    @handle_redis_errors(default_return=None)
    async def update_views_counter(self):
        async for key in self.connection.scan_iter("article_counter:*"):
            logger.debug("Found pending article view counter: %s", key)


    @handle_redis_errors(default_return=None)
    async def set_cache(
        self, record_selection: str, unique_record_identifier: str | int, record_details: dict, ttl: int = 3600
    ) -> None:
        cache_key = f"{record_selection}:{unique_record_identifier}"
        await self.connection.hset(cache_key, mapping=record_details)
        await self.connection.expire(cache_key, ttl)


    @handle_redis_errors(default_return=None)
    async def get_cached_user(self, unique_record_identifier: int | str) -> UserEntity | None:
        from_cache = cast(dict[str, str], await self.connection.hgetall(f"user:{unique_record_identifier}"))
        if not from_cache:
            return None
        return UserEntity(
            user_id=int(from_cache["user_id"]),
            email=from_cache["email"],
            unique_username=from_cache["unique_username"],
            nickname=from_cache["nickname"],
            subscriptions=json.loads(from_cache["subscriptions"]),
        )


    @handle_redis_errors(default_return=None)
    async def get_cached_article(self, article_id: int) -> ArticleEntity | None:
        from_cache = cast(
            dict[str, str],
            await self.connection.hgetall(f"article:{article_id}"),
        )
        if not from_cache:
            return None

        return ArticleEntity(
            unique_username=from_cache["unique_username"],
            title=from_cache["title"],
            content=from_cache["content"],
            user_id=int(from_cache["user_id"]),
            nickname=from_cache["nickname"],
            category=from_cache["category"],
            created_at=datetime.fromtimestamp(float(from_cache["created_at"])),
            article_id=int(from_cache["article_id"]),
            likes=int(from_cache["likes"]),
            dislikes=int(from_cache["dislikes"]),
        )


    @handle_redis_errors(default_return=None)
    async def delete_user(
        self,
        user: UserEntity,
    ):
        result = await self.connection.delete(
            f"user:{user.user_id}", f"user:{user.unique_username}"
        )
        return result


    @handle_redis_errors(default_return=None)
    async def delete_article(self, article_id: int) -> int | None:
        result = await self.connection.delete(f"article:{article_id}")
        return result
