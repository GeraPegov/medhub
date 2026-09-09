import asyncio
import logging

from app.infrastructure.database.connection import (
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


async def main():
    init_logger()
    await init_production_db()
    await init_test_db()


if __name__ == "__main__":
    asyncio.run(main())
