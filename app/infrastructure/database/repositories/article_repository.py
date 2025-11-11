from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.article import ArticleEntity
from app.domain.interfaces.repositories import IArticleRepository
from app.infrastructure.database.models.article import Article


class ArticleRepository(IArticleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session


    async def save_db(self, entity: ArticleEntity):
        article = Article(
            title=entity.title,
            content=entity.content,
            author_id=entity.author_id,
            author=entity.author
        )
        self.session.add(article)
        await self.session.commit()
        await self.session.refresh(article)
        return [ArticleEntity(
            id=article.id,
            title=article.title,
            content=article.content,
            date_add=article.date_add,
            author_id=article.author_id,
            author=article.author
        )]


    async def last_article_db(self):
        orm_article = await self.session.execute(
            select(Article).order_by(Article.id.desc()).limit(1)
        )
        article = orm_article.scalar_one()
        return ArticleEntity(
            id=article.id,
            title=article.title,
            content=article.content,
            date_add=article.date_add,
            author_id=article.author_id,
            author=article.author
        )


    async def search_by_title_db(self, title: str) -> list[ArticleEntity]:

        orm_article = await self.session.execute(
            select(Article).where(Article.title.ilike(f'%{title}%'))
        )
        articles = orm_article.scalars().all()

        return [
            ArticleEntity(
                id=article.id,
                title=article.title,
                content=article.content,
                author=article.author,
                date_add=article.date_add,
                author_id=article.author_id)
                for article in articles
        ]

    async def list_user_articles_db(self, id: int) -> list[ArticleEntity]:
        orm_articles = await self.session.execute(
            select(Article)
            .where(Article.author_id==id)
        )
        articles = orm_articles.scalars().all()

        return [
            ArticleEntity(
                id=article.id,
                title=article.title,
                content=article.content,
                author=article.author,
                date_add=article.date_add,
                author_id=article.author_id)
                for article in articles
        ]

    async def delete_article_db(self, id: int):
        orm_del = await self.session.execute(
            delete(Article)
            .where(Article.id==id)
            .returning(Article.title)
        )
        title = orm_del.scalar_one()
        await self.session.commit()
        return {"success delete": title}





