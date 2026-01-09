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

    async def check_limited(self, user_id: int):
        today = datetime.now().date()
        quanity_publication = (await self.session.execute(
            select(func.count(Article.id))
            .where(Article.user_id==user_id)
            .where(func.date(Article.created_at)==today)
        ))

        result = quanity_publication.scalar_one()
        return True if result < 3 else False

