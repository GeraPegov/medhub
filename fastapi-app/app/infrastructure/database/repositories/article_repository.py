import logging
from collections.abc import Sequence

from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.exceptions import (
    NotFoundArticleError,
    NotFoundUserError,
    ReactionAlreadyExistsError,
)
from app.domain.interfaces.article_repository import IArticleRepository
from app.domain.read_models import ArticleReadModel
from app.infrastructure.database.models.article import Article
from app.infrastructure.database.models.reaction import Reaction
from app.infrastructure.database.models.user import User

logger = logging.getLogger(__name__)


class ArticleRepository(IArticleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, mapping: dict, user_id: int) -> int:
        user_orm = (
            await self.session.execute(select(User).where(User.id == user_id))
        ).scalar_one_or_none()

        if user_orm is None:
            logger.warning(
                "Нельзя создать статью: пользователь не найден: user_id=%s",
                user_id,
            )
            raise NotFoundUserError

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

        return article.id

    async def get_by_id(self, article_id: int) -> ArticleReadModel:
        db_article = await self.session.execute(
            select(Article)
            .options(selectinload(Article.users))
            .where(Article.id == article_id)
        )
        articles = db_article.scalars().all()
        if not articles:
            logger.warning("Статья с article_id = %d не найдена", article_id)
            raise NotFoundArticleError
        read_models = self._to_read_model(articles)
        return read_models[0]

    async def all(self) -> list[ArticleReadModel] | None:
        db_articles = await self.session.execute(
            select(Article).options(selectinload(Article.users))
        )
        articles = db_articles.scalars().all()

        if not articles:
            logger.info("Не нашлось ни одной статьи при запросе вернуть все статьи.")
            return None
        return self._to_read_model(articles)

    async def delete(self, article_id: int, user_id: int) -> None:
        deleted_title = (
            await self.session.execute(
                delete(Article)
                .where(Article.id == article_id, Article.user_id == user_id)
                .returning(Article.title)
            )
        ).scalar_one_or_none()

        if deleted_title is None:
            await self.session.rollback()
            raise NotFoundArticleError()

        await self.session.commit()

    async def search_by_title(self, title: str) -> list[ArticleReadModel] | None:
        title = title.strip()
        similarity = func.strict_word_similarity(title, Article.title)

        db_articles = await self.session.execute(
            select(Article)
            .options(selectinload(Article.users))
            .where(
                or_(
                    Article.title.ilike(f"%{title}%"),
                    Article.title.op("%>>")(title),
                )
            )
            .order_by(similarity.desc(), Article.id.desc())
        )
        articles = db_articles.scalars().all()
        if not articles:
            logger.info("Не нашлось статей по заголовку = %s", title)
            return None
        return self._to_read_model(articles)

    async def get_user_articles(self, user_id: int) -> list[ArticleReadModel] | None:
        db_articles = await self.session.execute(
            select(Article)
            .options(selectinload(Article.users))
            .where(Article.user_id == int(user_id))
        )
        articles = db_articles.scalars().all()
        if not articles:
            return None
        return self._to_read_model(articles)

    async def search_by_category(self, category: str) -> list[ArticleReadModel] | None:
        db_articles = await self.session.execute(
            select(Article)
            .options(selectinload(Article.users))
            .where(Article.category == category)
        )
        articles = db_articles.scalars().all()
        if not articles:
            logger.info("Статьи по категории не найдены: category=%s", category)
            return None
        return self._to_read_model(articles)

    async def change(
        self,
        mapping: dict,
        article_id: int,
        user_id: int,
    ) -> ArticleReadModel:
        updated_article_id = (
            await self.session.execute(
                update(Article)
                .where(Article.id == article_id, Article.user_id == user_id)
                .values(
                    title=mapping["title"],
                    content=mapping["content"],
                    category=mapping["category"],
                )
                .returning(Article.id)
            )
        ).scalar_one_or_none()
        if updated_article_id is None:
            await self.session.rollback()
            raise NotFoundArticleError()

        await self.session.commit()
        return await self.get_by_id(updated_article_id)

    async def set_reaction(
        self, article_id: int, user_id: int, reaction: str
    ) -> ArticleReadModel:
        reaction_counters = {
            "like": Article.like,
            "dislike": Article.dislike,
        }
        counter = reaction_counters[reaction]

        updated_article = (
            await self.session.execute(
                update(Article)
                .where(Article.id == article_id)
                .values(**{reaction: counter + 1})
                .returning(Article.id)
            )
        ).scalar_one_or_none()

        if updated_article is None:
            await self.session.rollback()
            raise NotFoundArticleError()

        new_reaction = await self.session.execute(
            insert(Reaction)
            .values(user_id=user_id, article_id=article_id, reaction_type=reaction)
            .on_conflict_do_nothing(constraint="uq_reactions_user_article")
            .returning(Reaction.id)
        )
        reaction_id = new_reaction.scalar_one_or_none()
        if reaction_id is None:
            await self.session.rollback()
            raise ReactionAlreadyExistsError
        await self.session.commit()

        return await self.get_by_id(updated_article)

    async def liked_articles_by_user(
        self, user_id: int
    ) -> list[ArticleReadModel] | None:
        reaction_orm = await self.session.execute(
            select(Reaction)
            .options(selectinload(Reaction.articles).selectinload(Article.users))
            .where(
                Reaction.user_id == user_id,
                Reaction.reaction_type == "like",
            )
        )

        reaction = reaction_orm.scalars().all()
        only_articles = [reaction_item.articles for reaction_item in reaction]
        return self._to_read_model(only_articles) if only_articles else None

    def _to_read_model(self, articles: Sequence[Article]) -> list[ArticleReadModel]:
        return [
            ArticleReadModel(
                likes=article.like,
                dislikes=article.dislike,
                article_id=article.id,
                title=article.title,
                content=article.content,
                created_at=article.created_at,
                user_id=article.user_id,
                category=article.category,
                author_username=article.users.unique_username,
                author_nickname=article.users.nickname,
            )
            for article in articles
        ]
