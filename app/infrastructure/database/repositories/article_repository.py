from collections.abc import Sequence

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.database.models.user import article_likes
from app.domain.entities.article import ArticleEntity
from app.domain.interfaces.articleRepositories import IArticleRepository
from app.infrastructure.database.models.article import Article
from app.infrastructure.database.models.user import User


class ArticleRepository(IArticleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session


    async def save(self, mapping: dict, user_id: int) -> ArticleEntity:
        user_orm = (await self.session.execute(
            select(User)
            .where(User.id==user_id)
        )).scalar_one()
        articles = Article(
            title=mapping['title'],
            content=mapping['content'],
            user_id=mapping['user_id'],
            user=user_orm,
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
            .options(selectinload(Article.user))
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
            .options(selectinload(Article.user))
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
            .options(selectinload(Article.user))
            .where(Article.title.ilike(f'%{title}%'))
        )
        articles = orm_articles.scalars().all()

        return await self._to_entity(articles) if articles else None


    async def get_user_articles(self, user_id: int) -> list[ArticleEntity] | None:
        orm_articles = await self.session.execute(
            select(Article)
            .options(selectinload(Article.user))
            .where(Article.user_id==int(user_id))
        )
        articles = orm_articles.scalars().all()
        if not articles:
            return None
        return await self._to_entity(articles)


    async def search_by_category(self, category: str) -> list[ArticleEntity] | None:
        orm_articles = await self.session.execute(
            select(Article)
            .options(selectinload(Article.user))
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
            .options(selectinload(Article.user))
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


    async def set_reaction(
            self,
            article_id: int,
            user_id: int,
            reaction: str
    ):
        article = await self.session.get(Article, article_id)
        if not article:
            return {"success": False, "error": "Article not found"}

        user = await self.session.get(User, user_id)
        if not user:
            return {"success": False, "error": "User not found"}

        await self.session.execute(
            article_likes.insert().values(
                user_id=user_id,
                article_id=article_id,
                reaction_type=reaction
            )
        )

        if reaction == 'like':
            article.like += 1
        elif reaction == 'dislike':
            article.dislike += 1


    async def _to_entity(self, articles: Sequence[Article]) -> list[ArticleEntity]:
        return [ArticleEntity(
                    likes=article.like,
                    dislikes=article.dislike,
                    article_id=article.id,
                    title=article.title,
                    content=article.content,
                    unique_username=article.user.unique_username,
                    nickname=article.user.nickname,
                    created_at=article.created_at,
                    user_id=article.user_id,
                    category=article.category)
                    for article in articles]
