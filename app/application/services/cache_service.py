
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
                cash: CachedRepository,
                repo_user: UserRepository | None = None,
                repo_article: ArticleRepository | None = None
                ):
        self.cash = cash
        self.repo_user = repo_user
        self.repo_article = repo_article

    async def create_cache(
            self,
            action: str,
            key: str | int,
            mapping: dict
    ):
        try:
            await self.cash.create_cache(action, key, mapping)
        except:
            "хочу здесь обработать исключение, чтобы программа не остановилась если не получится сохранить кэш(типа обработать любую ошибку redis)"



    async def get_cache_user(
            self,
            key
    ) -> UserEntity | None:
        result = await self.cash.get_cache_user(key)
        logger.info(f'KEY IN CASHED USER {type(key) is str}, RESULT {result}')
        if not result and type(key) is str:
            logger.info('FRIST DO IT')
            result = await self.repo_user.get_by_username(key)
            if result:
                mapping = {
                    'user_id': result.user_id,
                    'email': result.email,
                    'unique_username': result.unique_username,
                    'nickname': result.nickname,
                    'subscriptions': json.dumps(result.subscriptions)
                }
                await self.create_cache(
                    'user',
                    key = result.unique_username,
                    mapping=mapping
                )
        elif not result and type(key) is int:
            result = await self.repo_user.get_by_id(key)
            logger.info('TWICE DO IT')
            if result:
                mapping = {
                    'user_id': result.user_id,
                    'email': result.email,
                    'unique_username': result.unique_username,
                    'nickname': result.nickname,
                    'subscriptions': json.dumps(result.subscriptions)
                }
                await self.create_cache(
                    'user',
                    key = result.user_id,
                    mapping=mapping
                )

        return result

    async def get_cache_article(
            self,
            key: int
    ) -> ArticleEntity | None:
        result = await self.cash.get_cache_article(key)
        if not result:
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
                await self.create_cache(
                    'article',
                    key = result.article_id,
                    mapping=mapping
                )

        return result
