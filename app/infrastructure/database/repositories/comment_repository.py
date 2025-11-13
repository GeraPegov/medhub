from multiprocessing.connection import Client

from sqlalchemy import delete, select

from app.domain.entities.comment import CommentEntity
from app.domain.interfaces.repositories import AsyncSession, ICommentRepository
from app.infrastructure.database.models.article import Article
from app.infrastructure.database.models.client import Client
from app.infrastructure.database.models.comment import Comment


class CommentRepository(ICommentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity: CommentEntity) -> CommentEntity:
        author_orm = await self.session.execute(
            select(Client)
            .where(Client.id==entity.author_id)
        )
        article_orm = await self.session.execute(
            select(Article)
            .where(Article.id==entity.article_id)
        )

        comment = Comment(
            content=entity.content,
            author_id=entity.author_id,
            article_id=entity.article_id,
            author=author_orm,
            article=article_orm,
        )

        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)

        return CommentEntity(
            id=comment.id,
            author_id=comment.author_id,
            article_id=comment.article_id,
            content=comment.content,
            datetime=comment.created_at,
            author=comment.author.username
        )

    async def show(self, article_id: int) -> list[CommentEntity]:
        comments_orm = await self.session.execute(
            select(Comment)
            .where(Comment.article_id==article_id)
        )

        comments = comments_orm.scalars().all()

        return [CommentEntity(
            id=comment.id,
            author_id=comment.author_id,
            article_id=comment.article_id,
            content=comment.content,
            datetime=comment.created_at,
            author=comment.author.username
        ) for comment in comments]


    async def delete(self, article_id: int):
        comments_del_orm = await self.session.execute(
            delete(Comment)
            .where(Comment.article_id==article_id)
            .returning(Comment.article.title)
        )
        comments_del = comments_del_orm.scalar_one()

        return comments_del

