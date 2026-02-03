from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.domain.entities.comment import CommentEntity
from app.domain.interfaces.comment_repositories import AsyncSession, ICommentRepository
from app.infrastructure.database.models.article import Article
from app.infrastructure.database.models.comment import Comments
from app.infrastructure.database.models.user import User


class CommentRepository(ICommentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, mapping: dict) -> CommentEntity:
        user_orm = (await self.session.execute(
            select(User)
            .where(User.id==mapping['user_id'])
        )).scalar_one()

        article_orm = (await self.session.execute(
            select(Article)
            .where(Article.id==mapping['article_id'])
        )).scalar_one()

        comment = Comments(
            content=mapping['content'],
            user_id=mapping['user_id'],
            article_id=mapping['article_id'],
            user=user_orm,
            article=article_orm,
        )

        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)

        comments = await self._to_entity([comment])
        return comments[0]

    async def show_by_article(self, article_id: int) -> list[CommentEntity] | None:
        comments_orm = await self.session.execute(
            select(Comments)
            .options(selectinload(Comments.user))
            .options(selectinload(Comments.article))
            .where(Comments.article_id==int(article_id))
        )

        comments = comments_orm.scalars().all()

        return await self._to_entity(comments) if comments else None

    async def show_by_author(self, user_id: int) -> list[CommentEntity] | None:
        comments_orm = await self.session.execute(
            select(Comments)
            .options(selectinload(Comments.user))
            .options(selectinload(Comments.article))
            .where(Comments.user_id==user_id)
        )

        comments = comments_orm.scalars().all()

        return await self._to_entity(comments) if comments else None


    async def delete(self, comment_id: int) -> int | None:
        comments_del_orm = await self.session.execute(
            delete(Comments)
            .where(Comments.id==comment_id)
            .returning(Comments.article_id)
        )
        article_id = comments_del_orm.scalar_one()
        await self.session.commit()

        return article_id if article_id else None

    async def _to_entity(self, entity: Sequence[Comments]):
        return [CommentEntity(
            id=comment.id,
            title_of_article=comment.article.title,
            user_id=comment.user_id,
            article_id=comment.article_id,
            content=comment.content,
            created_at=comment.created_at,
            nickname=comment.user.nickname,
            unique_username=comment.user.unique_username
        ) for comment in entity]
