from datetime import  date, datetime

from sqlalchemy import and_
from sqlalchemy.sql import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interfaces.logic_repository import ILogicRepository
from app.infrastructure.database.models.article import Article
from app.infrastructure.database.models.user import User, article_likes


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

    
    async def check_reaction(self, user_id: int, article_id: int):
        current_reaction_result = await self.session.execute(
            select(article_likes.c.created_at)
            .where(
                and_(
                    article_likes.c.user_id==user_id,
                    article_likes.c.article_id==article_id
                )
            )
        )
        current_reaction = current_reaction_result.scalar_one_or_none()
        result = True
        if current_reaction.date() == (func.now()).date():
            result = None
            
        return {
            'result': result,
            'created_at': current_reaction.date()
        }