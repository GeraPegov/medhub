from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.domain.entities.comment import CommentEntity
from app.domain.interfaces.commentRepositories import AsyncSession, ICommentRepository
from app.domain.logging import logger
from app.infrastructure.database.models.article import Article
from app.infrastructure.database.models.client import Client
from app.infrastructure.database.models.comment import Comment


class CommentRepository(ICommentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, author_id: int, article_id: int, content: str) -> CommentEntity:
        logger.info('start DB COMMENT')
        author_orm = (await self.session.execute(
            select(Client)
            .where(Client.id==author_id)
        )).scalar_one()
        article_orm = (await self.session.execute(
            select(Article)
            .where(Article.id==article_id)
        )).scalar_one()
        comment = Comment(
            content=content,
            author_id=author_id,
            article_id=article_id,
            author=author_orm,
            article=article_orm,
        )

        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)
        logger.info('finish COMMENT')
        return CommentEntity(
            id=comment.id,
            author_id=comment.author_id,
            article_id=comment.article_id,
            content=comment.content,
            created_at=comment.created_at,
            author=comment.author.username
        )

    async def show(self, article_id: int) -> list[CommentEntity]:
        comments_orm = await self.session.execute(
            select(Comment)
            .options(selectinload(Comment.author))
            .where(Comment.article_id==article_id)
        )

        comments = comments_orm.scalars().all()

        return [CommentEntity(
            id=comment.id,
            author_id=comment.author_id,
            article_id=comment.article_id,
            content=comment.content,
            created_at=comment.created_at,
            author=comment.author.username
        ) for comment in comments]


    async def delete(self, article_id: int):
        comments_del_orm = await self.session.execute(
            delete(Comment)
            .options(selectinload(Comment.article))
            .where(Comment.article_id==article_id)
            .returning(Comment.article.title)
        )
        comments_del = comments_del_orm.scalar_one()

        return comments_del

