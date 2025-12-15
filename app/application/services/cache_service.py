
import json

from app.domain.entities.article import ArticleEntity
from app.domain.entities.user import UserEntity
from app.domain.logging import logger
from app.infrastructure.database.repositories.article_repository import (
    ArticleRepository,
)
from app.infrastructure.database.repositories.cache_repository import CachedRepository
from app.infrastructure.database.repositories.user_repository import UserRepository


class CachedService:
    def __init__(self,
                cache: CachedRepository,
                repo_user: UserRepository | None = None,
                repo_article: ArticleRepository | None = None
                ):
        self.cache = cache
        self.repo_user = repo_user
        self.repo_article = repo_article

    async def _safe_cache(
            self,
            action: str,
            key: str | int,
            mapping: dict,
            ttl: int = 3600
    ):
        try:
            await self.cache.create_cache(action, key, mapping, ttl)
        except Exception as e:
            logger.error(f"Failed to cache {action}:{key}: {e}")

    async def update_user(
            self,
            user: UserEntity
    ):
        await self.cache.delete_user(user)
        mapping = {
                'user_id': user.user_id,
                'email': user.email,
                'unique_username': user.unique_username,
                'nickname': user.nickname,
                'subscriptions': json.dumps(list(user.subscriptions))
            }
        await self._safe_cache(
            'user',
            user.unique_username,
            mapping=mapping
        )
        return True

    async def get_cache_user(
            self,
            key
    ) -> UserEntity | None:
        result = await self.cache.get_cache_user(key)
        if result:
            return result

        if isinstance(key, str):
            result = await self.repo_user.get_by_username(key)
            cache_key = result.unique_username if result else None
        else:
            result = await self.repo_user.get_by_id(key)
            cache_key = result.user_id if result else None

        if result and cache_key:
            mapping = {
                'user_id': result.user_id,
                'email': result.email,
                'unique_username': result.unique_username,
                'nickname': result.nickname,
                'subscriptions': json.dumps(list(result.subscriptions))
            }
            await self._safe_cache(
                'user',
                cache_key,
                mapping=mapping
            )
        return result

    async def get_cache_article(
            self,
            key: int
    ) -> ArticleEntity | None:
        result = await self.cache.get_cache_article(key)
        if result:
            return result

        result = await self.repo_article.get_by_id(key)
        if result:
            mapping = {
                'unique_username': result.unique_username,
                'title': result.title,
                'content': result.content,
                'author_id': result.author_id,
                'nickname': result.nickname,
                'created_at': result.created_at.timestamp(),
                'category': result.category,
                'article_id': result.article_id
            }
            await self._safe_cache(
                'article',
                key,
                mapping=mapping
            )

        return result
