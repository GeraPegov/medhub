import json
from datetime import datetime

from redis.asyncio import Redis

from app.domain.entities.article import ArticleEntity
from app.domain.entities.user import UserEntity


class CachedRepository:
    def __init__(
            self,
            connection: Redis
        ):
        self.connection = connection


    async def create_cache(
            self,
            action: str,
            key: str | int,
            mapping: dict,
            ttl: int = 3600
    ) -> bool:
        cache_key = f"{action}:{key}"
        await self.connection.hset(cache_key, mapping=mapping)
        await self.connection.expire(cache_key, ttl)

        return True

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

    async def get_cache_article(
            self,
            key: int
    ) -> ArticleEntity | None:
        from_cache = await self.connection.hgetall(f'article:{key}')
        if not  from_cache:
            return None

        return ArticleEntity(
            unique_username = from_cache['unique_username'],
            title = from_cache['title'],
            content = from_cache['content'],
            user_id = from_cache['user_id'],
            nickname = from_cache['nickname'],
            category = from_cache['category'],
            created_at = datetime.fromtimestamp(float(from_cache['created_at'])),
            article_id = int(from_cache['article_id'])
        )

    async def delete_user(
            self,
            user: UserEntity
    ):
        result = await self.connection.delete(f'user:{user.user_id}', f'user:{user.unique_username}')
        return result

    async def delete_article(
            self,
            article_id: int
    ) -> int:
        result = await self.connection.delete(f'article:{article_id}')
        return result
