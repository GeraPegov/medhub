from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.article_service import ArticleService
from app.domain.interfaces.articleRepositories import IArticleRepository
from app.domain.interfaces.logic_repository import ILogicRepository
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.repositories.article_repository import (
    ArticleRepository,
)
from app.infrastructure.database.repositories.logic_repository import LogicRepository


def get_article_repository(
        session: AsyncSession = Depends(get_db)
) -> IArticleRepository:
    return ArticleRepository(session)

def get_logic_repository(
        session: AsyncSession = Depends(get_db)
) -> ILogicRepository:
    return LogicRepository(session)

def get_article_manager(
        base_repository: IArticleRepository = Depends(get_article_repository),
        logic_repository: ILogicRepository = Depends(get_logic_repository)
) -> ArticleService:
    return ArticleService(base_repository, logic_repository)
