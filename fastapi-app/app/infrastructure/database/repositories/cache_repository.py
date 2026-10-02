import json
import logging
from collections.abc import Awaitable, Callable
from datetime import datetime
from functools import wraps
from typing import Any, ParamSpec, TypeVar, cast

from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

from app.domain.entities.user import UserEntity
from app.domain.read_models import ArticleReadModel, CommentReadModel

logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


def handle_redis_errors(default_return: Any = None):
    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T | Any]]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except (RedisConnectionError, RedisTimeoutError) as error:
                logger.warning(
                    "Ошибка Redis, используется резервное поведение: operation=%s error=%s",
                    func.__name__,
                    error,
                )
                return default_return

        return wrapper

    return decorator


class CachedRepository:
    def __init__(self, connection: Redis):
        self.connection = connection

    @handle_redis_errors(default_return=None)
    async def set_cache(
        self,
        record_selection: str,
        unique_record_identifier: str | int,
        record_details: dict | list,
        ttl: int = 3600,
    ) -> None:
        cache_key = f"{record_selection}:{unique_record_identifier}"
        if isinstance(record_details, list):
            data = json.dumps(record_details)
            await self.connection.set(cache_key, data, ex=ttl)
            return

        await self.connection.hset(cache_key, mapping=record_details)
        await self.connection.expire(cache_key, ttl)

    @handle_redis_errors(default_return=None)
    async def get_cached_comments_for_article(
        self, article_id: int
    ) -> list[CommentReadModel] | None:
        raw_comments = await self.connection.get(f"comments:{article_id}")
        if not raw_comments:
            return None
        comments_data = json.loads(raw_comments)
        return [
            CommentReadModel(
                id=comment["id"],
                content=comment["content"],
                user_id=comment["user_id"],
                author_nickname=comment["author_nickname"],
                author_username=comment["author_username"],
                created_at=datetime.fromtimestamp(comment["created_at"]),
                article_id=comment["article_id"],
            )
            for comment in comments_data
        ]

    @handle_redis_errors(default_return=None)
    async def get_cached_user(
        self, unique_record_identifier: int | str
    ) -> UserEntity | None:
        users_data = cast(
            dict[str, str],
            await self.connection.hgetall(f"user:{unique_record_identifier}"),
        )
        if not users_data:
            return None
        return UserEntity(
            user_id=int(users_data["user_id"]),
            email=users_data["email"],
            unique_username=users_data["unique_username"],
            nickname=users_data["nickname"],
            subscriptions=json.loads(users_data["subscriptions"]),
        )

    @handle_redis_errors(default_return=None)
    async def get_cached_article(self, article_id: int) -> ArticleReadModel | None:
        articles_data = cast(
            dict[str, str],
            await self.connection.hgetall(f"article:{article_id}"),
        )
        if not articles_data:
            return None

        user_id = int(articles_data["user_id"])
        return ArticleReadModel(
            title=articles_data["title"],
            content=articles_data["content"],
            user_id=user_id,
            category=articles_data["category"],
            created_at=datetime.fromtimestamp(float(articles_data["created_at"])),
            article_id=int(articles_data["article_id"]),
            likes=int(articles_data["likes"]),
            dislikes=int(articles_data["dislikes"]),
            author_username=articles_data["unique_username"],
            author_nickname=articles_data["nickname"],
        )

    @handle_redis_errors(default_return=None)
    async def delete_user(
        self,
        user: UserEntity,
    ) -> None:
        deleted_keys = await self.connection.delete(
            f"user:{user.user_id}", f"user:{user.unique_username}"
        )
        logger.debug(
            "Удалён кеш пользователя: user_id=%s username=%s deleted_keys=%s",
            user.user_id,
            user.unique_username,
            deleted_keys,
        )

    @handle_redis_errors(default_return=None)
    async def delete_article(self, article_id: int) -> None:
        deleted_keys = await self.connection.delete(f"article:{article_id}")
        logger.debug(
            "Удалён кеш статьи: article_id=%d, deleted_keys=%s",
            article_id,
            deleted_keys,
        )

    @handle_redis_errors(default_return=None)
    async def delete_comments(self, article_id: int) -> None:
        deleted_keys = await self.connection.delete(f"comments:{article_id}")
        logger.debug(
            "Удалён кеш комментариев: article_id=%d, deleted_keys=%s",
            article_id,
            deleted_keys,
        )
