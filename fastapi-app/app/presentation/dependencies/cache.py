from collections.abc import AsyncGenerator

from fastapi import Depends
from redis.asyncio import Redis

from app.application.services.cache_service import (
    CachedArticleService,
    CachedUserService,
)
from app.infrastructure.database.repositories.article_repository import (
    ArticleRepository,
)
from app.infrastructure.database.repositories.cache_repository import CachedRepository
from app.infrastructure.database.repositories.logic_repository import LogicRepository
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.presentation.dependencies.articles_dependencies import (
    get_article_repository,
    get_logic_repository,
)
from app.presentation.dependencies.auth import get_user_repository

redis_pool = None


async def get_redis() -> AsyncGenerator[Redis, None]:
    if redis_pool is None:
        raise RuntimeError("Redis pool not initialized")
    r = Redis(connection_pool=redis_pool)
    try:
        yield r
    finally:
        await r.aclose()


async def get_cache_repository(connect: Redis = Depends(get_redis)) -> CachedRepository:
    return CachedRepository(connect)


async def get_cached_user_service(
    cache: CachedRepository = Depends(get_cache_repository),
    user_repository: UserRepository = Depends(get_user_repository),
) -> CachedUserService:
    return CachedUserService(cache=cache, user_repository=user_repository)


async def get_cached_article_service(
    cache: CachedRepository = Depends(get_cache_repository),
    article_repository: ArticleRepository = Depends(get_article_repository),
    logic_repository: LogicRepository = Depends(get_logic_repository),
) -> CachedArticleService:
    return CachedArticleService(
        cache=cache,
        article_repository=article_repository,
        logic_repository=logic_repository,
    )
