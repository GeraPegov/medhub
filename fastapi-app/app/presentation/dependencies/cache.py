from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

from app.application.services.cache_service import (
    CachedServiceArticle,
    CachedServiceUser,
)
from app.infrastructure.config import settings
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_pool
    redis_pool = ConnectionPool.from_url(
        f'redis://{settings.HOST_REDIS}:{settings.PORT_REDIS}',
        decode_responses=True,
        encoding='utf-8',
        max_connections=10,
        socket_timeout=1.0,
        socket_connect_timeout=1.0,
        retry_on_timeout=False
        )
    yield

    await redis_pool.aclose()

async def get_redis() -> AsyncGenerator[Redis, None]:
    if redis_pool is None:
        raise RuntimeError('Redis pool not initialized')
    r = Redis(connection_pool=redis_pool)
    try:
        yield r
    finally:
        await r.aclose()

async def get_cache_repository(
        connect: Redis = Depends(get_redis)
) -> CachedRepository:
    return CachedRepository(connect)


async def get_cache_user(
    cache: CachedRepository = Depends(get_cache_repository),
    repo_user: UserRepository = Depends(get_user_repository)
        ):
    return CachedServiceUser(
        cache=cache,
        repo_user = repo_user
    )

async def get_cache_article(
    cache: CachedRepository = Depends(get_cache_repository),
    repo_article: ArticleRepository = Depends(get_article_repository),
    repo_logic: LogicRepository = Depends(get_logic_repository)
        ):
    return CachedServiceArticle(
        cache=cache,
        repo_article=repo_article,
        repo_logic=repo_logic
    )
