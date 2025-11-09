from fastapi import APIRouter

from app.presentation.api.endpoints.auth import router as register_router
from app.presentation.api.endpoints.home import router as home_router
from app.presentation.api.endpoints.search_article import router as searchArticle_router
from app.presentation.api.endpoints.submit_article import router as submitArticle_router

api_router = APIRouter()

api_router.include_router(home_router, tags=["Home"])
api_router.include_router(submitArticle_router, tags=['Submit'])
api_router.include_router(searchArticle_router, tags=['Search'])
api_router.include_router(register_router, tags=['Register'])
