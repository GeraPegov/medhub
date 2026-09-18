from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, select

from app.domain.interfaces.logic_repository import ILogicRepository
from app.infrastructure.database.models.article import Article
from app.infrastructure.database.models.comment import Comment
from app.domain.exceptions import PublicationLimitError


class LogicRepository(ILogicRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def can_publish_article_today(self, user_id: int) -> None:
        today = datetime.now().date()
        publication_count = await self.session.execute(
            select(func.count(Article.id))
            .where(Article.user_id == user_id)
            .where(func.date(Article.created_at) == today)
        )

        result = publication_count.scalar_one()
        if result >= 3:
            raise PublicationLimitError

    async def can_publish_comment_today(self, user_id: int, article_id: int) -> None:
        current_time = datetime.now().replace(minute=0, second=0, microsecond=0)
        plus_hour = current_time + timedelta(hours=1)

        publication_count = await self.session.execute(
            select(func.count(Comment.id))
            .where(Comment.user_id == user_id)
            .where(Comment.article_id == article_id)
            .where(Comment.created_at < plus_hour)
            .where(Comment.created_at >= current_time)
        )

        result = publication_count.scalar_one()
        if result >= 10:
            raise PublicationLimitError
