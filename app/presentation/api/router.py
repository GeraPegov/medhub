from fastapi import APIRouter

from app.presentation.api.endpoints.comments import router as comments_router
from app.presentation.api.endpoints.exit import router as exit_router
from app.presentation.api.endpoints.home import router as home_router
from app.presentation.api.endpoints.login import router as login_router
from app.presentation.api.endpoints.only_article import router as only_article_router
from app.presentation.api.endpoints.register import router as register_router
from app.presentation.api.endpoints.search_article import (
    router as search_article_router,
)
from app.presentation.api.endpoints.submit_article import (
    router as submit_article_router,
)
from app.presentation.api.endpoints.user import router as user_router

api_router = APIRouter()

api_router.include_router(home_router, tags=["Home"])
api_router.include_router(submit_article_router, tags=['Submit'])
api_router.include_router(search_article_router, tags=['Search'])
api_router.include_router(register_router, tags=['Register'])
api_router.include_router(login_router, tags=['Login'])
api_router.include_router(user_router, tags=['UserArticles'])
api_router.include_router(only_article_router, tags=['Show'])
api_router.include_router(comments_router, tags=['Comments'])
api_router.include_router(exit_router, tags=['Exit'])
