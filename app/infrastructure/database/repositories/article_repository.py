from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.application.dto.articleCreate_dto import ArticleCreateDTO
from app.domain.entities.article import ArticleEntity
from app.domain.interfaces.articleRepositories import IArticleRepository
from app.domain.logging import logger
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
        articles = [Article(
            title=dto.title,
            content=dto.content,
            author_id=author_id,
            author=author_orm,
            category=dto.category
        )]
        self.session.add(articles)
        await self.session.commit()
        await self.session.refresh(articles)

        return await self._to_entity(articles)


    async def show(self, article_id: int) -> list[ArticleEntity]:
        orm_article = await self.session.execute(
            select(Article)
            .options(selectinload(Article.author))
            .where(Article.id==article_id)
        )
        articles = [orm_article.scalar_one()]

        return await self._to_entity(articles)


    async def delete(self, article_id: int) -> dict:
        orm_del = await self.session.execute(
            delete(Article)
            .where(Article.id == article_id)
            .returning(Article.title)
        )
        title = orm_del.scalar_one()
        await self.session.commit()
        return {"success delete": title}


    async def last_article(self) -> list[ArticleEntity]:
        orm_article = await self.session.execute(
            select(Article)
            .options(selectinload(Article.author))
            .order_by(Article.id.desc()).limit(1)
        )
        articles = [orm_article.scalar_one()]
        logger.info(f'THIS IS ARTICLES BEFORE SCALARS {articles}')

        return await self._to_entity(articles)


    async def search_by_title(self, title: str) -> list[ArticleEntity]:
        orm_articles = await self.session.execute(
            select(Article)
            .options(selectinload(Article.author))
            .where(Article.title.ilike(f'%{title}%'))
        )
        articles = orm_articles.scalars().all()

        return await self._to_entity(articles)


    async def get_user_articles(self, user_id: int) -> list[ArticleEntity] | None:
        orm_articles = await self.session.execute(
            select(Article)
            .options(selectinload(Article.author))
            .where(Article.author_id==user_id)
        )
        articles = orm_articles.scalars().all()
        if not articles:
            return None
        return await self._to_entity(articles)

    async def _to_entity(self, articles: Sequence[Article]) -> list[ArticleEntity]:
        logger.info(f'start to entity {articles}')
        return [ArticleEntity(
                    id=article.id,
                    title=article.title,
                    content=article.content,
                    username=article.author.unique_username,
                    nickname=article.author.nickname,
                    created_at=article.created_at,
                    author_id=article.author_id,
                    category=article.category)
                    for article in articles]
