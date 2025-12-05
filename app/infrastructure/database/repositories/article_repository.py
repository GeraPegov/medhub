from collections.abc import Sequence

from sqlalchemy import delete, select, update
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


    async def save(self, dto: ArticleCreateDTO, author_id: int) -> ArticleEntity:
        author_orm = (await self.session.execute(
            select(Client)
            .where(Client.id==author_id)
        )).scalar_one()
        articles = Article(
            title=dto.title,
            content=dto.content,
            author_id=author_id,
            author=author_orm,
            category=dto.category
        )
        self.session.add(articles)
        await self.session.commit()
        await self.session.refresh(articles)

        entities = await self._to_entity([articles])
        return entities[0]


    async def get_by_id(self, article_id: int) -> ArticleEntity:
        orm_article = await self.session.execute(
            select(Article)
            .options(selectinload(Article.author))
            .where(Article.id==article_id)
        )
        articles = orm_article.scalars().all()

        entities = await self._to_entity(articles)
        return entities[0]


    async def all(self) -> list[ArticleEntity] | None:
        orm_articles = await self.session.execute(
            select(Article)
            .options(selectinload(Article.author))
        )
        articles = orm_articles.scalars().all()

        if not articles:
            return None
        return await self._to_entity(articles)


    async def delete(self, article_id: int) -> dict:
        orm_del = await self.session.execute(
            delete(Article)
            .where(Article.id==article_id)
            .returning(Article.title)
        )
        title = orm_del.scalar_one()
        await self.session.commit()
        return {"success delete": title}


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


    async def search_by_category(self, category: str) -> list[ArticleEntity] | None:
        orm_articles = await self.session.execute(
            select(Article)
            .options(selectinload(Article.author))
            .where(Article.category==category)
        )
        articles = orm_articles.scalars().all()
        if not articles:
            return None
        return await self._to_entity(articles)

    async def change(self, dto: ArticleCreateDTO, article_id: int) -> ArticleEntity | None:
        orm_articles = await self.session.execute(
            update(Article)
            .where(Article.id==article_id)
            .options(selectinload(Article.author))
            .values(
                title=dto.title,
                content=dto.content,
                category=dto.category
            )
            .returning(Article)
        )
        await self.session.commit()

        articles = orm_articles.scalars().all()
        if not articles:
            return None
        entities = await self._to_entity(articles)
        return entities[0]


    async def _to_entity(self, articles: Sequence[Article]) -> list[ArticleEntity]:
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
