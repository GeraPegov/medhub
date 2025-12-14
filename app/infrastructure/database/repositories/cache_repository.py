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
            action,
            key,
            mapping
    ):
        await self.connection.hmset(f'{action}:{key}', mapping=mapping)
        self.connection.expire(f'user:{key}', 3600)
        return True

    async def get_cache_user(
            self, key
    ) -> UserEntity | None:
        from_cache = await self.connection.hgetall(f'user:{key}')
        if from_cache:
            return UserEntity(
                user_id = int(from_cache['user_id']),
                email = from_cache['email'],
                unique_username = from_cache['unique_username'],
                nickname = from_cache['nickname'],
                subscriptions = json.loads(from_cache['subscriptions'])
            )
        return None

    async def get_cache_article(
            self,
            key: int
    ) -> ArticleEntity | None:
        from_cache = await self.connection.hgetall(f'article:{key}')
        if from_cache:
            return ArticleEntity(
                unique_username = from_cache['unique_username'],
                title = from_cache['title'],
                content = from_cache['content'],
                author_id = from_cache['author_id'],
                nickname = from_cache['nickname'],
                category = from_cache['category'],
                created_at = datetime.fromtimestamp(float(from_cache['created_at'])),
                article_id = int(from_cache['article_id'])
            )
        return None
