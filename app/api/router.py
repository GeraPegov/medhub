from fastapi import APIRouter


from app.api.endpoints.home import router as home_router
from app.api.endpoints.search_article import router as searchArticle_router
from app.api.endpoints.submit_article import router as submitArticle_router
from app.api.endpoints.register import router as register_router

api_router = APIRouter()

api_router.include_router(home_router, tags=["Home"])
api_router.include_router(submitArticle_router, tags=['Submit'])
api_router.include_router(searchArticle_router, tags=['Search'])
api_router.include_router(register_router, tags=['Register'])
