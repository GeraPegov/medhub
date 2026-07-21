from collections.abc import Sequence
from datetime import datetime
from dataclasses import dataclass

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.article import ArticleEntity
from app.domain.interfaces.article_repository import IArticleRepository
from app.infrastructure.database.models.article import Article
from app.infrastructure.database.models.reaction import Reaction
from app.infrastructure.database.models.user import User

@dataclass
class Response_reaction:
    reaction: Article
    date_of_rection: datetime

class ArticleRepository(IArticleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session


    async def save(self, mapping: dict, user_id: int) -> ArticleEntity:
        user_orm = (await self.session.execute(
            select(User)
            .where(User.id==user_id)
        )).scalar_one()
        article = Article(
            title=mapping['title'],
            content=mapping['content'],
            user_id=mapping['user_id'],
            users=user_orm,
            category=mapping['category']
        )

        self.session.add(article)
        await self.session.commit()
        await self.session.refresh(article)

        entities = await self._to_entity([article])
        return entities[0]


    async def get_by_id(self, article_id: int) -> ArticleEntity | None:
        db_article = await self.session.execute(
            select(Article)
            .options(selectinload(Article.users))
            .where(Article.id==article_id)
        )
        articles = db_article.scalars().all()
        if not articles:
            return None
        entities = await self._to_entity(articles)
        return entities[0]


    async def all(self) -> list[ArticleEntity] | None:
        db_articles = await self.session.execute(
            select(Article)
            .options(selectinload(Article.users))
        )
        articles = db_articles.scalars().all()

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
        db_articles = await self.session.execute(
            select(Article)
            .options(selectinload(Article.user))
            .where(Article.title.ilike(f'%{title}%'))
        )
        articles = db_articles.scalars().all()

        return await self._to_entity(articles) if articles else None


    async def get_user_articles(self, user_id: int) -> list[ArticleEntity] | None:
        db_articles = await self.session.execute(
            select(Article)
            .options(selectinload(Article.users))
            .where(Article.user_id==int(user_id))
        )
        articles = db_articles.scalars().all()
        if not articles:
            return None
        return await self._to_entity(articles)


    async def search_by_category(self, category: str) -> list[ArticleEntity] | None:
        db_articles = await self.session.execute(
            select(Article)
            .options(selectinload(Article.users))
            .where(Article.category==category)
        )
        articles = db_articles.scalars().all()
        if not articles:
            return None
        return await self._to_entity(articles)


    async def change(self, mapping: dict, article_id: int) -> ArticleEntity | None:
        db_articles = await self.session.execute(
            update(Article)
            .where(Article.id==article_id)
            .options(selectinload(Article.users))
            .values(
                title=mapping['title'],
                content=mapping['content'],
                category=mapping['category']
            )
            .returning(Article)
        )
        await self.session.commit()

        articles = db_articles.scalars().all()
        if not articles:
            return None
        entities = await self._to_entity(articles)
        return entities[0]

    async def check_reaction(self, article_id: int, user_id: int) -> bool:
        check = (await self.session.execute(
            select(Reaction.id)
            .filter((Reaction.article_id==article_id) & (Reaction.user_id==user_id))
        )).scalar_one_or_none()

        return True if check else False


    async def set_reaction(
            self,
            article_id: int,
            user_id: int,
            reaction: str
    ) -> Response_reaction:
        field_name = {
            "like": Article.like,
            "dislike": Article.dislike
        }
        new_reaction = Reaction(
            user_id=user_id,
            article_id=article_id,
            reaction_type=reaction
        )
        new_record_with_reaction = (await self.session.execute(
                update(Article)
                .options(selectinload(Article.users))
                .where(Article.id == article_id)
                .values(**{reaction: field_name[reaction] + 1})
                .returning(Article)
                )).scalar_one()

        self.session.add(new_reaction)
        await self.session.commit()
        new_record = await self._to_entity([new_record_with_reaction])
        return {
            'reaction': new_record[0],
            'date_of_reaction': new_reaction.created_at
        }

    async def liked_articles_by_user(self, user_id: int):
        reaction_orm = await self.session.execute(
            select(Reaction)
            .options(selectinload(Reaction.articles).selectinload(Article.users))
            .where(Reaction.user_id==user_id)
        )

        reaction = reaction_orm.scalars().all()
        only_articles = [article.article for article in reaction]
        return await self._to_entity(only_articles) if only_articles else None


    async def _to_entity(self, articles: Sequence[Article]) -> list[ArticleEntity]:
        return [ArticleEntity(
                    likes=article.like,
                    dislikes=article.dislike,
                    article_id=article.id,
                    title=article.title,
                    content=article.content,
                    unique_username=article.users.unique_username,
                    nickname=article.users.nickname,
                    created_at=article.created_at,
                    user_id=article.user_id,
                    category=article.category)
                    for article in articles]
