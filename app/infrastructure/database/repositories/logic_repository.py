from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, select

from app.domain.interfaces.logic_repository import ILogicRepository
from app.infrastructure.database.models.article import Article


class LogicRepository(ILogicRepository):
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session

    async def can_publish_today(self, user_id: int):
        today = datetime.now().date()
        publication_count = (await self.session.execute(
            select(func.count(Article.id))
            .where(Article.user_id==user_id)
            .where(func.date(Article.created_at)==today)
        ))

        result = publication_count.scalar_one()
        return True if result < 3 else False

