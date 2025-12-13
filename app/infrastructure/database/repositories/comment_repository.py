from typing import Sequence
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.domain.entities.comment import CommentEntity
from app.domain.interfaces.commentRepositories import AsyncSession, ICommentRepository
from app.infrastructure.database.models.article import Article
from app.infrastructure.database.models.comment import Comments
from app.infrastructure.database.models.user import User


class CommentRepository(ICommentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, author_id: int, article_id: int, content: str) -> CommentEntity:
        author_orm = (await self.session.execute(
            select(User)
            .where(User.id==author_id)
        )).scalar_one()
        article_orm = (await self.session.execute(
            select(Article)
            .where(Article.id==article_id)
        )).scalar_one()
        comment = Comments(
            content=content,
            author_id=author_id,
            article_id=article_id,
            author=author_orm,
            article=article_orm,
        )

        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)

        comments = await self._to_entity([comment])

        return comments[0]

    async def show_by_article(self, article_id: int) -> list[CommentEntity]:
        comments_orm = await self.session.execute(
            select(Comments)
            .options(selectinload(Comments.author))
            .where(Comments.article_id==article_id)
        )

        comments = comments_orm.scalars().all()

        return await self._to_entity(comments)

    async def show_by_author(self, user_id: int) -> list[CommentEntity]:
        comments_orm = await self.session.execute(
            select(Comments)
            .options(selectinload(Comments.author))
            .where(Comments.author_id==user_id)
        )

        comments = comments_orm.scalars().all()

        return await self._to_entity(comments)


    async def delete(self, comment_id: int):
        comments_del_orm = await self.session.execute(
            delete(Comments)
            .where(Comments.id==comment_id)
            .returning(Comments.article_id)
        )
        article_id = comments_del_orm.scalar_one()
        await self.session.commit()

        return article_id

    async def _to_entity(self, entity: Sequence):
        return [CommentEntity(
            id=comment.id,
            author_id=comment.author_id,
            article_id=comment.article_id,
            content=comment.content,
            created_at=comment.created_at,
            nickname=comment.author.nickname,
            unique_username=comment.author.unique_username
        ) for comment in entity]