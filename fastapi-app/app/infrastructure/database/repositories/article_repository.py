from collections.abc import Sequence

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.article import ArticleEntity
from app.domain.exceptions import ArticleNotFoundError, ReactionAlreadyExistsError
from app.domain.interfaces.article_repository import IArticleRepository
from app.infrastructure.database.models.article import Article
from app.infrastructure.database.models.reaction import Reaction
from app.infrastructure.database.models.user import User


class ArticleRepository(IArticleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, mapping: dict, user_id: int) -> ArticleEntity:
        user_orm = (
            await self.session.execute(select(User).where(User.id == user_id))
        ).scalar_one()
        article = Article(
            title=mapping["title"],
            content=mapping["content"],
            user_id=mapping["user_id"],
            users=user_orm,
            category=mapping["category"],
        )

        self.session.add(article)
        await self.session.commit()
        await self.session.refresh(article)

        entities = await self._to_entity([article])
        return entities[0]

    async def get_by_id(self, article_id: int) -> ArticleEntity:
        db_article = await self.session.execute(
            select(Article)
            .options(selectinload(Article.users))
            .where(Article.id == article_id)
        )
        articles = db_article.scalars().all()
        if not articles:
            raise ArticleNotFoundError
        entities = await self._to_entity(articles)
        return entities[0]

    async def all(self) -> list[ArticleEntity] | None:
        db_articles = await self.session.execute(
            select(Article).options(selectinload(Article.users))
        )
        articles = db_articles.scalars().all()

        if not articles:
            return None
        return await self._to_entity(articles)

    async def delete(self, article_id: int, user_id: int) -> bool:
        deleted_title = (
            await self.session.execute(
                delete(Article)
                .where(Article.id == article_id, Article.user_id == user_id)
                .returning(Article.title)
            )
        ).scalar_one_or_none()

        if deleted_title is None:
            await self.session.rollback()
            raise ArticleNotFoundError()

        await self.session.commit()
        return True

    async def search_by_title(self, title: str) -> list[ArticleEntity] | None:
        db_articles = await self.session.execute(
            select(Article)
            .options(selectinload(Article.users))
            .where(Article.title.ilike(f"%{title}%"))
        )
        articles = db_articles.scalars().all()

        return await self._to_entity(articles) if articles else None

    async def get_user_articles(self, user_id: int) -> list[ArticleEntity] | None:
        db_articles = await self.session.execute(
            select(Article)
            .options(selectinload(Article.users))
            .where(Article.user_id == int(user_id))
        )
        articles = db_articles.scalars().all()
        if not articles:
            return None
        return await self._to_entity(articles)

    async def search_by_category(self, category: str) -> list[ArticleEntity] | None:
        db_articles = await self.session.execute(
            select(Article)
            .options(selectinload(Article.users))
            .where(Article.category == category)
        )
        articles = db_articles.scalars().all()
        if not articles:
            return None
        return await self._to_entity(articles)

    async def change(
        self,
        mapping: dict,
        article_id: int,
        user_id: int,
    ) -> ArticleEntity:
        db_articles = await self.session.execute(
            update(Article)
            .where(Article.id == article_id, Article.user_id == user_id)
            .options(selectinload(Article.users))
            .values(
                title=mapping["title"],
                content=mapping["content"],
                category=mapping["category"],
            )
            .returning(Article)
        )
        articles = db_articles.scalars().all()
        if not articles:
            await self.session.rollback()
            raise ArticleNotFoundError()

        await self.session.commit()
        entities = await self._to_entity(articles)
        return entities[0]

    async def set_reaction(
        self, article_id: int, user_id: int, reaction: str
    ) -> ArticleEntity:
        reaction_counters = {
            "like": Article.like,
            "dislike": Article.dislike,
        }
        counter = reaction_counters[reaction]

        new_reaction = Reaction(
            user_id=user_id,
            article_id=article_id,
            reaction_type=reaction,
        )
        updated_article = (
            await self.session.execute(
                update(Article)
                .options(selectinload(Article.users))
                .where(Article.id == article_id)
                .values(**{reaction: counter + 1})
                .returning(Article)
            )
        ).scalar_one_or_none()

        if updated_article is None:
            await self.session.rollback()
            raise ArticleNotFoundError()

        self.session.add(new_reaction)
        try:
            await self.session.commit()
        except IntegrityError as error:
            await self.session.rollback()
            constraint_name = getattr(
                getattr(error.orig, "diag", None),
                "constraint_name",
                None,
            ) or getattr(
                getattr(error.orig, "__cause__", None),
                "constraint_name",
                None,
            )
            if constraint_name == "uq_reactions_user_article":
                raise ReactionAlreadyExistsError() from error
            raise

        articles = await self._to_entity([updated_article])
        return articles[0]

    async def liked_articles_by_user(self, user_id: int):
        reaction_orm = await self.session.execute(
            select(Reaction)
            .options(selectinload(Reaction.articles).selectinload(Article.users))
            .where(Reaction.user_id == user_id)
        )

        reaction = reaction_orm.scalars().all()
        only_articles = [reaction_item.articles for reaction_item in reaction]
        return await self._to_entity(only_articles) if only_articles else None

    async def _to_entity(self, articles: Sequence[Article]) -> list[ArticleEntity]:
        return [
            ArticleEntity(
                likes=article.like,
                dislikes=article.dislike,
                article_id=article.id,
                title=article.title,
                content=article.content,
                unique_username=article.users.unique_username,
                nickname=article.users.nickname,
                created_at=article.created_at,
                user_id=article.user_id,
                category=article.category,
            )
            for article in articles
        ]
