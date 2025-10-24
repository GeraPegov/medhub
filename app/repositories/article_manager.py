from pydantic import HttpUrl
from app.core.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.core.models.article import Article


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

class ArticleManager():
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_article(self, author, title, content):
        try:
            new_article = Article(author=author, title=title, content=content)
            self.session.add(new_article)
            await self.session.commit()
            await self.session.refresh(new_article)
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(500, f"ошибка базы данных {str(e)}")