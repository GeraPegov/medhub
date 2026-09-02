from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.comment import CommentEntity
from app.domain.exceptions import (
    NotFoundArticleError,
    NotFoundCommentError,
    NotFoundUserError,
)
from app.domain.interfaces.comment_repository import ICommentRepository
from app.infrastructure.database.models.article import Article
from app.infrastructure.database.models.comment import Comment
from app.infrastructure.database.models.user import User


class CommentRepository(ICommentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, mapping: dict) -> CommentEntity:
        user_orm = (
            await self.session.execute(
                select(User).where(User.id == mapping["user_id"])
            )
        ).scalar_one_or_none()

        if user_orm is None:
            raise NotFoundUserError

        article_orm = (
            await self.session.execute(
                select(Article).where(Article.id == mapping["article_id"])
            )
        ).scalar_one_or_none()
        if article_orm is None:
            raise NotFoundArticleError

        comment = Comment(
            content=mapping["content"],
            user_id=mapping["user_id"],
            article_id=mapping["article_id"],
            users=user_orm,
            articles=article_orm,
        )

        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)

        comments = await self._to_entity([comment])
        return comments[0]

    async def list_by_article_id(self, article_id: int) -> list[CommentEntity] | None:
        comments_orm = await self.session.execute(
            select(Comment)
            .options(selectinload(Comment.users))
            .options(selectinload(Comment.articles))
            .where(Comment.article_id == int(article_id))
        )

        comments = comments_orm.scalars().all()

        return await self._to_entity(comments) if comments else None

    async def list_by_author(self, user_id: int) -> list[CommentEntity] | None:
        comments_orm = await self.session.execute(
            select(Comment)
            .options(selectinload(Comment.users))
            .options(selectinload(Comment.articles))
            .where(Comment.user_id == user_id)
        )

        comments = comments_orm.scalars().all()

        return await self._to_entity(comments) if comments else None

    async def delete(self, comment_id: int, user_id: int) -> int:
        comments_del_orm = await self.session.execute(
            delete(Comment)
            .where(Comment.id == comment_id, Comment.user_id == user_id)
            .returning(Comment.article_id)
        )
        article_id = comments_del_orm.scalar_one_or_none()
        if article_id is None:
            raise NotFoundCommentError
        await self.session.commit()
        return article_id

    async def _to_entity(self, entity: Sequence[Comment]):
        return [
            CommentEntity(
                id=comment.id,
                title_of_article=comment.articles.title,
                user_id=comment.user_id,
                article_id=comment.article_id,
                content=comment.content,
                created_at=comment.created_at,
                nickname=comment.users.nickname,
                unique_username=comment.users.unique_username,
            )
            for comment in entity
        ]
