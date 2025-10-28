from app.core.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models.pydantic import ArticleModel

from app.core.models.article import Article


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()



class ArticleRepository():
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, article: Article):
        try:
            self.session.add(article)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(500, f"ошибка базы данных {str(e)}")


            


