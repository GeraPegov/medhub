import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from redis.asyncio.connection import ConnectionPool
from starlette.middleware.sessions import SessionMiddleware

import app.presentation.dependencies.cache as state
from app.infrastructure.config import settings
from app.infrastructure.logging_config import init_logger
from app.presentation.api.router import api_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_logger()
    state.redis_pool = ConnectionPool.from_url(
        f"redis://{settings.HOST_REDIS}:{settings.PORT_REDIS}",
        decode_responses=True,
        encoding="utf-8",
        max_connections=10,
        socket_timeout=1.0,
        socket_connect_timeout=1.0,
        retry_on_timeout=False,
    )
    logger.info("Запуск приложения")
    yield
    logger.info("Остановка приложения")
    if state.redis_pool is not None:
        await state.redis_pool.aclose()
        state.redis_pool = None


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates("app/presentation/api/endpoints/templates")

app.mount(
    "/static",
    StaticFiles(directory="app/presentation/api/endpoints/templates"),
    name="static",
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY_MIDDLEWARE,
    session_cookie="medhub_session",
    same_site="lax",
    https_only=True,
)

app.include_router(api_router)
