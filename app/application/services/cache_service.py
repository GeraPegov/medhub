
import json
from typing import Optional

from app.domain.entities.article import ArticleEntity
from app.domain.entities.user import UserEntity
from app.domain.logging import logger
from app.infrastructure.database.repositories.article_repository import (
    ArticleRepository,
)
from app.infrastructure.database.repositories.cache_repository import CachedRepository
from app.infrastructure.database.repositories.logic_repository import LogicRepository
from app.infrastructure.database.repositories.user_repository import UserRepository


class BasedCachedService:
    def __init__(self, cache: CachedRepository):
        self.cache = cache

    async def _safe_cache(
            self,
            key: str | int,
            mapping: dict,
            action: str,
            ttl: int = 3600
    ):
        await self.cache.create_cache(action, key, mapping, ttl)



class CachedServiceUser(BasedCachedService):
    def __init__(self,
                cache: CachedRepository,
                repo_user: UserRepository
                ):
        super().__init__(cache)
        self.repo_user = repo_user

    async def update_user(
            self,
            user: UserEntity
    ):
        await self.cache.delete_user(user)
        mapping = {
                'user_id': str(user.user_id),
                'email': user.email,
                'unique_username': user.unique_username,
                'nickname': user.nickname,
                'subscriptions': json.dumps(list(user.subscriptions))
            }
        await self._safe_cache(
            user.unique_username,
            mapping=mapping,
            action='user'
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
                cache_key,
                mapping=mapping,
                action='user'
            )
        return result


class CachedServiceArticle(BasedCachedService):
    def __init__(self,
                cache: CachedRepository,
                repo_article: ArticleRepository,
                repo_logic: LogicRepository
                ):
        super().__init__(cache)
        self.repo_article = repo_article
        self.repo_logic = repo_logic

    async def get_cache_article(
            self,
            key: int,
            user_id: int | None = None
    ) -> ArticleEntity | None:
        result = await self.cache.get_cache_article(key)
        if result:
            if user_id:
                reaction = await self.repo_logic.check_reaction(
                    user_id=user_id,
                    article_id=key
                )
                result.reaction = reaction
            return result

        result = await self.repo_article.get_by_id(key)
        if result:
            mapping = {
                'unique_username': result.unique_username,
                'title': result.title,
                'content': result.content,
                'user_id': result.user_id,
                'nickname': result.nickname,
                'created_at': result.created_at.timestamp(),
                'category': result.category,
                'article_id': result.article_id,
                'likes': result.likes,
                'dislike': result.dislikes
            }
            await self._safe_cache(
                key,
                mapping=mapping,
                action='article'
            )

        return result

    async def set_reaction(
            self,
            user_id: int,
            article_id: int,
            reaction: str
    ):
        result = await self.cache.get_reaction(user_id, article_id)

        if not result:
            check_reaction = await self.repo_logic.check_reaction(user_id, article_id)

            mapping = {
                'created_at': check_reaction['created_at']
            }

            await self._safe_cache(
                key=f'user{user_id}',
                action=f'article{article_id}',
                mapping=mapping
            )

            await self.repo_article.set_reaction(article_id, user_id, reaction)
        



        
            