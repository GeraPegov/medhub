
import pytest
import asyncio

from redis.asyncio.connection import ConnectionPool
from redis.asyncio import Redis

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.infrastructure.config import settings
from app.infrastructure.database.connection import Base

TEST_DATABASE_URL = settings.TEST_DB_URL

@pytest.fixture(scope='function')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope='function')
async def engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False
    )
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope='function')
async def db_session(engine):
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope='function')
async def db_redis():
    redis_pool = ConnectionPool.from_url(
        f'redis://{settings.HOST_REDIS}:{settings.PORT_REDIS}',
        decode_responses=True)
    redis = Redis(connection_pool=redis_pool)
    yield redis
    await redis.flushall()
    await redis.aclose()


