from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.article_service import ArticleService
from app.domain.interfaces.articleRepositories import IArticleRepository
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.repositories.article_repository import (
    ArticleRepository,
)


def get_article_repository(
        session: AsyncSession = Depends(get_db)
) -> IArticleRepository:
    return ArticleRepository(session)

def get_article_manager(
        repository: IArticleRepository = Depends(get_article_repository)
) -> ArticleService:
    return ArticleService(repository)
