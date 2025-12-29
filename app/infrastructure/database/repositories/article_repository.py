from collections.abc import Sequence

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.article import ArticleEntity
from app.domain.interfaces.articleRepositories import IArticleRepository
from app.infrastructure.database.models.article import Article
from app.infrastructure.database.models.user import User


class ArticleRepository(IArticleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session


    async def save(self, mapping: dict, author_id: int) -> ArticleEntity:
        author_orm = (await self.session.execute(
            select(User)
            .where(User.id==author_id)
        )).scalar_one()
        articles = Article(
            title=mapping['title'],
            content=mapping['content'],
            author_id=mapping['author_id'],
            author=author_orm,
            category=mapping['category']
        )

        self.session.add(articles)
        await self.session.commit()
        await self.session.refresh(articles)

        entities = await self._to_entity([articles])
        return entities[0]


    async def get_by_id(self, article_id: int) -> ArticleEntity | None:
        orm_article = await self.session.execute(
            select(Article)
            .options(selectinload(Article.author))
            .where(Article.id==article_id)
        )
        articles = orm_article.scalars().all()
        if not articles:
            return None
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


    async def delete(self, article_id: int) -> bool:
        orm_del = await self.session.execute(
            delete(Article)
            .where(Article.id==article_id)
            .returning(Article.title)
        )
        orm_del.scalar_one()
        await self.session.commit()
        return True


    async def search_by_title(self, title: str) -> list[ArticleEntity] | None:
        orm_articles = await self.session.execute(
            select(Article)
            .options(selectinload(Article.author))
            .where(Article.title.ilike(f'%{title}%'))
        )
        articles = orm_articles.scalars().all()

        return await self._to_entity(articles) if articles else None


    async def get_user_articles(self, user_id: int) -> list[ArticleEntity] | None:
        orm_articles = await self.session.execute(
            select(Article)
            .options(selectinload(Article.author))
            .where(Article.author_id==int(user_id))
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


    async def change(self, mapping: dict, article_id: int) -> ArticleEntity | None:
        orm_articles = await self.session.execute(
            update(Article)
            .where(Article.id==article_id)
            .options(selectinload(Article.author))
            .values(
                title=mapping['title'],
                content=mapping['content'],
                category=mapping['category']
            )
            .returning(Article)
        )
        await self.session.commit()

        articles = orm_articles.scalars().all()
        if not articles:
            return None
        entities = await self._to_entity(articles)
        return entities[0]


    async def like(self, user_id: int, article_id: int) -> ArticleEntity:
        orm_article = await self.session.execute(
            select(Article)
            .where(Article.id==article_id)
        )


    async def _to_entity(self, articles: Sequence[Article]) -> list[ArticleEntity]:
        return [ArticleEntity(
                    article_id=article.id,
                    title=article.title,
                    content=article.content,
                    unique_username=article.author.unique_username,
                    nickname=article.author.nickname,
                    created_at=article.created_at,
                    author_id=article.author_id,
                    category=article.category)
                    for article in articles]
