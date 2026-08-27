import json

from app.domain.entities.article import ArticleEntity
from app.domain.entities.user import UserEntity
from app.infrastructure.database.repositories.article_repository import (
    ArticleRepository,
)
from app.infrastructure.database.repositories.cache_repository import CachedRepository
from app.infrastructure.database.repositories.logic_repository import LogicRepository
from app.infrastructure.database.repositories.user_repository import UserRepository


class BaseCachedService:
    def __init__(self, cache: CachedRepository):
        self.cache = cache

    async def _set_cache(
        self, key: str | int, mapping: dict, prefix: str, ttl: int = 3600
    ):
        await self.cache.set_cache(prefix, key, mapping, ttl)


class CachedUserService(BaseCachedService):
    def __init__(self, cache: CachedRepository, user_repository: UserRepository):
        super().__init__(cache)
        self.user_repository = user_repository

    async def update_user(self, user: UserEntity):
        await self.cache.delete_user(user)
        mapping = {
            "user_id": str(user.user_id),
            "email": user.email,
            "unique_username": user.unique_username,
            "nickname": user.nickname,
            "subscriptions": json.dumps(list(user.subscriptions)),
        }
        await self._set_cache(user.unique_username, mapping=mapping, prefix="user")
        return True

    async def get_user(self, key: int | str) -> UserEntity | None:
        result = await self.cache.get_cached_user(key)
        if result:
            return result

        if isinstance(key, str):
            result = await self.user_repository.get_by_username(key)
            cache_key = result.unique_username if result else None
        else:
            result = await self.user_repository.get_by_id(key)
            cache_key = result.user_id if result else None

        if result and cache_key:
            mapping = {
                "user_id": result.user_id,
                "email": result.email,
                "unique_username": result.unique_username,
                "nickname": result.nickname,
                "subscriptions": json.dumps(list(result.subscriptions)),
            }
            await self._set_cache(cache_key, mapping=mapping, prefix="user")
        return result


class CachedArticleService(BaseCachedService):
    def __init__(
        self,
        cache: CachedRepository,
        article_repository: ArticleRepository,
        logic_repository: LogicRepository,
    ):
        super().__init__(cache)
        self.article_repository = article_repository
        self.logic_repository = logic_repository

    async def get_article(self, article_id: int) -> ArticleEntity:
        cached_article = await self.cache.get_cached_article(article_id)
        if cached_article:
            return cached_article

        article = await self.article_repository.get_by_id(article_id)
        cache_data = {
            "unique_username": article.unique_username,
            "title": article.title,
            "content": article.content,
            "user_id": article.user_id,
            "nickname": article.nickname,
            "created_at": article.created_at.timestamp(),
            "category": article.category,
            "article_id": article.article_id,
            "likes": article.likes,
            "dislikes": article.dislikes,
        }
        await self._set_cache(article_id, mapping=cache_data, prefix="article")

        return article

    async def update_article(self, article: ArticleEntity):
        await self.cache.delete_article(article.article_id)
        mapping = {
            "unique_username": article.unique_username,
            "title": article.title,
            "content": article.content,
            "user_id": article.user_id,
            "nickname": article.nickname,
            "created_at": article.created_at.timestamp(),
            "category": article.category,
            "article_id": article.article_id,
            "likes": article.likes,
            "dislikes": article.dislikes,
        }
        await self._set_cache(article.article_id, mapping=mapping, prefix="article")
        return True

    async def delete_article(self, article_id: int):
        return await self.cache.delete_article(article_id)

    async def increment_view_counter(self, article_id: int):
        return await self.cache.increment_view_counter(article_id)

    async def update_views_counter(self):
        await self.cache.update_views_counter()

    async def add_reaction(
        self,
        user_id: int,
        article_id: int,
        reaction: str,
    ) -> dict[str, int]:
        article = await self.article_repository.set_reaction(
            article_id=article_id, user_id=user_id, reaction=reaction
        )
        await self.update_article(article)
        return {
            "likes": article.likes,
            "dislikes": article.dislikes,
        }
