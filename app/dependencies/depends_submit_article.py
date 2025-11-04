from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.domain.repositories import IArticleRepository
from app.repositories.article_repository import ArticleRepository
from app.services.article_manager import ArticleManager


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def get_article_repository(
        session: AsyncSession = Depends(get_db)
) -> IArticleRepository:
    return ArticleRepository(session)

def get_article_manager(
        repository: IArticleRepository = Depends(get_article_repository)
) -> ArticleManager:
    return ArticleManager(repository)

