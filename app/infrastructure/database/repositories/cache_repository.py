from functools import wraps
import json
from datetime import datetime
from typing import Any, Awaitable, ParamSpec, TypeVar
from collections.abc import Callable
from venv import logger
import asyncio 

from redis import RedisError
from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

from app.domain.entities.article import ArticleEntity
from app.domain.entities.user import UserEntity

P = ParamSpec('P')
T= TypeVar('T')

def handle_redis_errors(default_return: Any = None):
    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T | Any]]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except (RedisConnectionError, RedisTimeoutError) as e:
                logger.warning(f'Redis error in {func.__name__}: {e}')
                return default_return
            except Exception as e:
                logger.error(f'Unexpected error in {func.__name__}: {e}')
                return default_return
        return wrapper
    return decorator


class CachedRepository:
    def __init__(
            self,
            connection: Redis
        ):
        self.connection = connection


    @handle_redis_errors(default_return=None)
    async def create_cache(
            self,
            action: str,
            key: str | int,
            mapping: dict,
            ttl: int = 3600
    ) -> bool | None:
        cache_key = f"{action}:{key}"
        await self.connection.hset(cache_key, mapping=mapping)
        await self.connection.expire(cache_key, ttl)
        return True


    @handle_redis_errors(default_return=None)
    async def get_cache_user(
            self,
            key: int | str
    ) -> UserEntity | None:
        from_cache = await self.connection.hgetall(f'user:{key}')
        if not from_cache:
            return None
        return UserEntity(
            user_id = int(from_cache['user_id']),
            email = from_cache['email'],
            unique_username = from_cache['unique_username'],
            nickname = from_cache['nickname'],
            subscriptions = json.loads(from_cache['subscriptions'])
        )


    @handle_redis_errors(default_return=None)
    async def get_cache_article(
            self,
            key: int
    ) -> ArticleEntity | None:
        from_cache = await self.connection.hgetall(f'article:{key}')
        if not from_cache:
            return None
        return ArticleEntity(
            unique_username = from_cache['unique_username'],
            title = from_cache['title'],
            content = from_cache['content'],
            user_id = from_cache['user_id'],
            nickname = from_cache['nickname'],
            category = from_cache['category'],
            created_at = datetime.fromtimestamp(float(from_cache['created_at'])),
            article_id = int(from_cache['article_id']),
            likes = from_cache['likes'],
            dislikes = from_cache['dislikes']
        )


    @handle_redis_errors(default_return=None)
    async def delete_user(
            self,
            user: UserEntity,
    ):
        result = await self.connection.delete(f'user:{user.user_id}', f'user:{user.unique_username}')
        return result


    @handle_redis_errors(default_return=None)
    async def delete_article(
            self,
            article_id: int
    ) -> int | None:
        result = await self.connection.delete(f'article:{article_id}')
        return result
