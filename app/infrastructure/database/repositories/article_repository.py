from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.article import ArticleEntity
from app.domain.interfaces.repositories import IArticleRepository
from app.infrastructure.database.models.article import Article


class ArticleRepository(IArticleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session


    async def save(self, entity: ArticleEntity):
        article = Article(
            title=entity.title,
            content=entity.article,
            author_id=entity.author_id,
            author=entity.author
        )
        self.session.add(article)
        await self.session.commit()
        await self.session.refresh(article)
        return [ArticleEntity(
            title=article.title,
            article=article.content,
            date_add=article.date_add,
            author_id=article.author_id,
            author=article.author
        )]


    async def last_article(self):
        orm_article = await self.session.execute(
            select(Article).order_by(Article.id.desc()).limit(1)
        )
        article = orm_article.scalar_one()
        return ArticleEntity(
            title=article.title,
            article=article.content,
            date_add=article.date_add,
            author_id=article.author_id,
            author=article.author
        )


    async def search_by_title(self, title: str) -> list[ArticleEntity]:

        orm_article = await self.session.execute(
            select(Article).where(Article.title.ilike(f'%{title}%'))
        )
        article = orm_article.scalars().all()

        return [
            ArticleEntity(
                title=article.title,
                article=article.content,
                author=article.author,
                date_add=article.date_add,
                author_id=article.author_id)
                for article in article
        ]






