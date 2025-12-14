from fastapi import Depends
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

from app.application.services.cache_service import CachedService
from app.infrastructure.config import settings
from app.infrastructure.database.repositories.article_repository import (
    ArticleRepository,
)
from app.infrastructure.database.repositories.cache_repository import CachedRepository
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.presentation.dependencies.articles_dependencies import get_article_repository
from app.presentation.dependencies.auth import get_user_repository


async def get_redis():
    pool = ConnectionPool.from_url(
        f'redis://{settings.HOST_REDIS}:{settings.PORT_REDIS}',
        decode_responses=True)
    r = Redis(
        host=settings.HOST_REDIS,
        port=settings.PORT_REDIS,
        decode_responses=True
        )
    try:
        yield r
    finally:
        await r.aclose()
        await pool.aclose()

async def get_cash_repositories(
        connect: Redis = Depends(get_redis)
) -> CachedRepository:
    return CachedRepository(connect)



async def get_cache_user(
    cash: CachedRepository = Depends(get_cash_repositories),
    repo_user: UserRepository = Depends(get_user_repository)
        ):
    return CachedService(
        cash=cash,
        repo_user = repo_user
    )

async def get_cache_article(
    cash: CachedRepository = Depends(get_cash_repositories),
    repo_article: ArticleRepository = Depends(get_article_repository)
        ):
    return CachedService(
        cash=cash,
        repo_article=repo_article
    )
