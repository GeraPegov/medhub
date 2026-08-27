from contextlib import asynccontextmanager

from app.application.services.cache_service import CachedArticleService
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.repositories.article_repository import (
    ArticleRepository,
)
from app.infrastructure.database.repositories.cache_repository import CachedRepository
from app.infrastructure.database.repositories.logic_repository import LogicRepository
from app.presentation.dependencies.cache import get_redis


@asynccontextmanager
async def scheduler_service_context():
    redis_gen = get_redis()
    db_gen = get_db()

    redis = await anext(redis_gen)
    db = await anext(db_gen)

    try:
        yield CachedArticleService(
            cache=CachedRepository(redis),
            article_repository=ArticleRepository(db),
            logic_repository=LogicRepository(db),
        )
    finally:
        await redis_gen.aclose()
        await db_gen.aclose()
