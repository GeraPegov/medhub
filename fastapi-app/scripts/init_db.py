import asyncio
import logging

from sqlalchemy.ext.asyncio import create_async_engine

import app.infrastructure.database.models  # noqa: F401
from app.infrastructure.config import settings
from app.infrastructure.database.connection import (
    Base,
    create_database_if_not_exists,
    prod_engine,
)
from app.infrastructure.logging_config import init_logger

logger = logging.getLogger(__name__)


async def init_production_db():
    logger.info("initializing production database")

    await create_database_if_not_exists("medhub")

    # await create_tables(prod_engine)

    await prod_engine.dispose()


async def init_test_db():
    logger.info("initializing test database")

    await create_database_if_not_exists("testmedhub")


async def init_test_db_for_admin_services():
    logger.info("initializing test database for admin services")

    await create_database_if_not_exists("test_admin_services")

    test_admin_url = settings.TEST_DB_URL_FOR_ADMIN_SERVICES.replace(
        "postgresql://", "postgresql+asyncpg://", 1
    )
    engine = create_async_engine(test_admin_url, echo=False)
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def main():
    init_logger()
    await init_production_db()
    await init_test_db()
    await init_test_db_for_admin_services()


if __name__ == "__main__":
    asyncio.run(main())
