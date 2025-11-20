import redis
from fastapi import Depends
from redis import Redis

from app.infrastructure.config import settings
from app.infrastructure.database.repositories.cache_repository import CachedRepository
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.presentation.dependencies.auth import get_user_repository


def get_redis():
    r = redis.Redis(
        host=settings.HOST_REDIS,
        port=settings.PORT_REDIS,
        decode_responses=True)
    try:
        yield r
    finally:
        r.close()


async def get_cache_repositories(
        connect: Redis = Depends(get_redis),
        session: UserRepository = Depends(get_user_repository)
        ):
    return CachedRepository(connect, session)

