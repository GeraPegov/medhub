from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.application.dto.articleCreate_dto import ArticleCreateDTO
from app.domain.entities.article import ArticleEntity
from app.domain.interfaces.articleRepositories import IArticleRepository
from app.infrastructure.database.models.article import Article
from app.infrastructure.database.models.client import Client


class ArticleRepository(IArticleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session


    async def save(self, dto: ArticleCreateDTO, author_id: int) -> list[ArticleEntity]:
        author_orm = (await self.session.execute(
            select(Client)
            .where(Client.id==author_id)
        )).scalar_one()
        article = Article(
            title=dto.title,
            content=dto.content,
            author_id=author_id,
            author=author_orm
        )
        self.session.add(article)
        await self.session.commit()
        await self.session.refresh(article)

        return [ArticleEntity(
                    id=article.id,
                    title=article.title,
                    content=article.content,
                    author=article.author.username,
                    created_at=article.created_at,
                    author_id=article.author_id)]


    async def show(self, article_id: int) -> ArticleEntity:
        orm_article = await self.session.execute(
            select(Article)
            .options(selectinload(Article.author))
            .where(Article.id==article_id)
        )
        article = orm_article.scalar_one()

        return ArticleEntity(
            author=article.author.username,
            title=article.title,
            content=article.content,
            author_id=article.author_id,
            created_at=article.created_at,
            id=article.id
        )


    async def delete(self, article_id: int) -> dict:
        orm_del = await self.session.execute(
            delete(Article)
            .where(Article.id == article_id)
            .returning(Article.title)
        )
        title = orm_del.scalar_one()
        await self.session.commit()
        return {"success delete": title}


    async def last_article(self) -> ArticleEntity:
        orm_article = await self.session.execute(
            select(Article)
            .options(selectinload(Article.author))
            .order_by(Article.id.desc()).limit(1)
        )
        article = orm_article.scalar_one()
        return ArticleEntity(
            id=article.id,
            title=article.title,
            content=article.content,
            created_at=article.created_at,
            author_id=article.author_id,
            author=article.author.username
        )


    async def search_by_title(self, title: str) -> list[ArticleEntity]:
        orm_articles = await self.session.execute(
            select(Article)
            .options(selectinload(Article.author))
            .where(Article.title.ilike(f'%{title}%'))
        )
        articles = orm_articles.scalars().all()

        return [
            ArticleEntity(
                id=article.id,
                title=article.title,
                content=article.content,
                author=article.author.username,
                created_at=article.created_at,
                author_id=article.author_id)
                for article in articles
        ]


    async def get_user_articles(self, user_id: int) -> list[ArticleEntity]:
        orm_articles = await self.session.execute(
            select(Article)
            .options(selectinload(Article.author))
            .where(Article.author_id==user_id)
        )
        articles = orm_articles.scalars().all()

        return [
            ArticleEntity(
                id=article.id,
                title=article.title,
                content=article.content,
                author=article.author.username,
                created_at=article.created_at,
                author_id=article.author_id)
                for article in articles
        ]
