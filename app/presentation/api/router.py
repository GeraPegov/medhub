from fastapi import APIRouter

from app.presentation.api.endpoints.comments import router as comments_router
from app.presentation.api.endpoints.home import router as home_router
from app.presentation.api.endpoints.login import router as login_router
from app.presentation.api.endpoints.only_article import router as only_article__router
from app.presentation.api.endpoints.register import router as register_router
from app.presentation.api.endpoints.search_article import router as searchArticle_router
from app.presentation.api.endpoints.submit_article import router as submitArticle_router
from app.presentation.api.endpoints.user import router as userArticles_router

api_router = APIRouter()

api_router.include_router(home_router, tags=["Home"])
api_router.include_router(submitArticle_router, tags=['Submit'])
api_router.include_router(searchArticle_router, tags=['Search'])
api_router.include_router(register_router, tags=['Register'])
api_router.include_router(login_router, tags=['Login'])
api_router.include_router(userArticles_router, tags=['UserArticles'])
api_router.include_router(only_article__router, tags=['Show'])
api_router.include_router(comments_router, tags=['Comments'])
