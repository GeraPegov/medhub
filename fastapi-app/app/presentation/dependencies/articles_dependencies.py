import os
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.article_service import ArticleService
from app.domain.interfaces.article_repositories import IArticleRepository
from app.domain.interfaces.logic_repository import ILogicRepository
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.repositories.http_client import RateLimiterClient
from app.infrastructure.database.repositories.article_repository import (
    ArticleRepository,
)
from app.infrastructure.database.repositories.logic_repository import LogicRepository


_rate_limiter_client: RateLimiterClient | None = None


def get_rate_limiter() -> RateLimiterClient:
    """
    Возвращает singleton экземпляр RateLimiterClient.
    Создаётся один раз для всего приложения.
    """
    global _rate_limiter_client
    if _rate_limiter_client is None:
        _rate_limiter_client = RateLimiterClient(
            base_url=os.getenv("RATE_LIMITER_URL", "http://localhost:8080")
        )
    return _rate_limiter_client

def get_article_repository(
        session: AsyncSession = Depends(get_db)
) -> IArticleRepository:
    return ArticleRepository(session)


def get_logic_repository(
        session: AsyncSession = Depends(get_db)
) -> ILogicRepository:
    return LogicRepository(session)


def get_article_service(
        base_repository: IArticleRepository = Depends(get_article_repository),
        rate_client: RateLimiterClient = Depends(get_rate_limiter)
) -> ArticleService:
    return ArticleService(base_repository, rate_client)
