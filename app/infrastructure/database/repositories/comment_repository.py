from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.domain.entities.comment import CommentEntity
from app.domain.interfaces.commentRepositories import AsyncSession, ICommentRepository
from app.infrastructure.database.models.article import Article
from app.infrastructure.database.models.client import Client
from app.infrastructure.database.models.comment import Comments


class CommentRepository(ICommentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, author_id: int, article_id: int, content: str) -> CommentEntity:
        author_orm = (await self.session.execute(
            select(Client)
            .where(Client.id==author_id)
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

        return CommentEntity(
            id=comment.id,
            author_id=comment.author_id,
            article_id=comment.article_id,
            content=comment.content,
            created_at=comment.created_at,
            nickname=comment.author.nickname,
            username=comment.author.unique_username
        )

    async def show_by_article(self, article_id: int) -> list[CommentEntity]:
        comments_orm = await self.session.execute(
            select(Comments)
            .options(selectinload(Comments.author))
            .where(Comments.article_id==article_id)
        )

        comments = comments_orm.scalars().all()

        return [CommentEntity(
            id=comment.id,
            author_id=comment.author_id,
            article_id=comment.article_id,
            content=comment.content,
            created_at=comment.created_at,
            nickname=comment.author.nickname,
            username=comment.author.unique_username
        ) for comment in comments]

    async def show_by_author(self, client_id: int) -> list[CommentEntity]:
        comments_orm = await self.session.execute(
            select(Comments)
            .options(selectinload(Comments.author))
            .where(Comments.author_id==client_id)
        )

        comments = comments_orm.scalars().all()

        return [CommentEntity(
            id=comment.id,
            author_id=comment.author_id,
            article_id=comment.article_id,
            content=comment.content,
            created_at=comment.created_at,
            nickname=comment.author.nickname,
            username=comment.author.unique_username
        ) for comment in comments]


    async def delete(self, comment_id: int):
        comments_del_orm = await self.session.execute(
            delete(Comments)
            .where(Comments.id==comment_id)
            .returning(Comments.article_id)
        )
        article_id = comments_del_orm.scalar_one()
        await self.session.commit()

        return article_id


