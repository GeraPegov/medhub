from app.core.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import select

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
    
    async def last_article(self):
        try:
            result = await self.session.execute(
                select(Article).order_by(Article.id.desc()).limit(1)
            )
            articles = result.scalar_one_or_none()
            return articles
        except Exception as e:
            raise HTTPException(500, f'warning: {str(e)}')

    async def search_article(self, title):
        try:
            result = await self.session.execute(
                select(Article).where(Article.title.ilike(f'%{title}%'))
            )
            articles = result.scalars().all()
            return articles
        except Exception as e:
            raise HTTPException(500, f'warning {str(e)}')

            


