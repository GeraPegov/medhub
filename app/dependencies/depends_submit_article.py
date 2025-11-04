from app.domain.repositories import IArticleRepository
from app.models.pydantic import ArticleCreateDTO
from app.repositories.article_repository import ArticleRepository
from app.services.article_manager import ArticleManager
from fastapi import Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal

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
):
    return ArticleManager(repository)

async def parse_article_form(
        author: str = Form(),
        title: str = Form(),
        content: str = Form()
) -> ArticleCreateDTO:
    return ArticleCreateDTO(
        author=author,
        title=title,
        content=content
    )