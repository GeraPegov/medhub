from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.repositories import IArticleRepository
from app.domain.entities import ArticleEntity

from app.core.models.article import Article


class ArticleRepository(IArticleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, entity: ArticleEntity):
        article = Article(
            author=entity.author,
            title=entity.title,
            article=entity.article
        )
        self.session.add(article)
        await self.session.commit()
        await self.session.refresh(article)

        return [ArticleEntity(
            author=article.author,
            title=article.title,
            article=article.article,
            date_add=article.date_add
        )]

    
    async def last_article(self):
        result = await self.session.execute(
            select(Article).order_by(Article.id.desc()).limit(1)
        )
        orm_articles = result.scalar_one_or_none()
        return ArticleEntity(
                date_add=orm_articles.date_add,
                title=orm_articles.title,
                article=orm_articles.article,
                author=orm_articles.author)


    async def search_by_title(self, title: str) -> list[ArticleEntity]:

        result = await self.session.execute(
            select(Article).where(Article.title.ilike(f'%{title}%'))
        )
        orm_articles = result.scalars().all()

        return [
            ArticleEntity(
                title=article.title,
                article=article.article,
                author=article.author,
                date_add=article.date_add)
                for article in orm_articles
        ] 

            


