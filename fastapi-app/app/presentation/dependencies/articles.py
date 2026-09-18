from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.article_service import ArticleService
from app.domain.interfaces.article_repository import IArticleRepository
from app.domain.interfaces.logic_repository import ILogicRepository
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.repositories.article_repository import (
    ArticleRepository,
)
from app.presentation.dependencies.logic import get_logic_repository


async def get_article_repository(
    session: AsyncSession = Depends(get_db),
) -> IArticleRepository:
    return ArticleRepository(session)


async def get_article_service(
    base_repository: IArticleRepository = Depends(get_article_repository),
    logic_repository: ILogicRepository = Depends(get_logic_repository),
) -> ArticleService:
    return ArticleService(base_repository, logic_repository)
