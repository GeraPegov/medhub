import json

from app.domain.entities.user import UserEntity
from app.domain.exceptions import NotFoundUserError
from app.domain.read_models import ArticleReadModel, CommentReadModel
from app.infrastructure.database.repositories.article_repository import (
    ArticleRepository,
)
from app.infrastructure.database.repositories.cache_repository import CachedRepository
from app.infrastructure.database.repositories.comment_repository import (
    CommentRepository,
)
from app.infrastructure.database.repositories.user_repository import UserRepository


class BaseCachedService:
    def __init__(self, cache: CachedRepository):
        self.cache = cache

    async def _set_cache(
        self,
        record_selection: str,
        unique_record_identifier: str | int,
        record_details: dict | list,
        ttl: int = 3600,
    ) -> None:
        await self.cache.set_cache(
            record_selection, unique_record_identifier, record_details, ttl
        )


class CachedCommentService(BaseCachedService):
    def __init__(self, cache: CachedRepository, comment_repository: CommentRepository):
        super().__init__(cache)
        self.comment_repository = comment_repository

    async def get_comments_for_article(
        self, article_id: int
    ) -> list[CommentReadModel] | None:
        cached_comments = await self.cache.get_cached_comments_for_article(article_id)
        if cached_comments is not None:
            return cached_comments

        comments = await self.comment_repository.list_by_article_id(article_id)
        if comments is None:
            return None
        data = [
            {
                "id": comment.id,
                "content": comment.content,
                "user_id": comment.user_id,
                "author_nickname": comment.author_nickname,
                "author_username": comment.author_username,
                "created_at": comment.created_at.timestamp(),
                "article_id": comment.article_id,
            }
            for comment in comments
        ]
        await self._set_cache(
            record_selection="comments",
            unique_record_identifier=article_id,
            record_details=data,
        )

        return comments

    async def invalidate_comments(self, article_id: int) -> None:
        await self.cache.delete_comments(article_id)


class CachedUserService(BaseCachedService):
    def __init__(self, cache: CachedRepository, user_repository: UserRepository):
        super().__init__(cache)
        self.user_repository = user_repository

    async def update_user(self, user: UserEntity) -> None:
        await self.cache.delete_user(user)
        data = {
            "user_id": str(user.user_id),
            "email": user.email,
            "unique_username": user.unique_username,
            "nickname": user.nickname,
            "subscriptions": json.dumps(list(user.subscriptions)),
        }
        await self._set_cache(
            unique_record_identifier=user.user_id,
            record_selection="user",
            record_details=data,
        )

    async def get_user(self, key: int | str) -> UserEntity:
        cached_user = await self.cache.get_cached_user(key)
        if cached_user:
            return cached_user

        if isinstance(key, str):
            user = await self.user_repository.get_by_username(key)
            if user is None:
                raise NotFoundUserError
            cache_key = user.unique_username
        else:
            user = await self.user_repository.get_by_id(key)
            if user is None:
                raise NotFoundUserError
            cache_key = user.user_id

        if user and cache_key:
            data = {
                "user_id": user.user_id,
                "email": user.email,
                "unique_username": user.unique_username,
                "nickname": user.nickname,
                "subscriptions": json.dumps(list(user.subscriptions)),
            }
            await self._set_cache(
                record_selection="user",
                unique_record_identifier=cache_key,
                record_details=data,
            )
        return user

    async def invalidate_user(self, user: UserEntity) -> None:
        await self.cache.delete_user(user)

    async def delete_user(self, user: UserEntity) -> None:
        await self.user_repository.delete_profile(user.user_id)
        await self.invalidate_user(user)


class CachedArticleService(BaseCachedService):
    def __init__(
        self,
        cache: CachedRepository,
        article_repository: ArticleRepository,
    ):
        super().__init__(cache)
        self.article_repository = article_repository

    async def get_article(self, article_id: int) -> ArticleReadModel:
        cached_article = await self.cache.get_cached_article(article_id)
        if cached_article:
            return cached_article

        article = await self.article_repository.get_by_id(article_id)
        data = {
            "unique_username": article.author_username,
            "title": article.title,
            "content": article.content,
            "user_id": article.user_id,
            "nickname": article.author_nickname,
            "created_at": article.created_at.timestamp(),
            "category": article.category,
            "article_id": article.article_id,
            "likes": article.likes,
            "dislikes": article.dislikes,
        }
        await self._set_cache(
            record_selection="article",
            unique_record_identifier=article_id,
            record_details=data,
        )

        return article

    async def update_article(self, article: ArticleReadModel) -> None:
        await self.cache.delete_article(article.article_id)
        data = {
            "unique_username": article.author_username,
            "title": article.title,
            "content": article.content,
            "user_id": article.user_id,
            "nickname": article.author_nickname,
            "created_at": article.created_at.timestamp(),
            "category": article.category,
            "article_id": article.article_id,
            "likes": article.likes,
            "dislikes": article.dislikes,
        }
        await self._set_cache(
            record_selection="article",
            unique_record_identifier=article.article_id,
            record_details=data,
        )

    async def invalidate_article(self, article_id: int) -> None:
        await self.cache.delete_article(article_id)
        await self.cache.delete_comments(article_id)

    async def delete_article(self, article_id: int, current_user_id: int) -> None:
        await self.article_repository.delete(article_id, current_user_id)
        await self.invalidate_article(article_id)

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
