from fastapi import APIRouter

from app.presentation.api.endpoints.admin import router as admin_router
from app.presentation.api.endpoints.articles import router as articles_router
from app.presentation.api.endpoints.auth import router as auth_router
from app.presentation.api.endpoints.comments import router as comments_router
from app.presentation.api.endpoints.pages import router as pages_router
from app.presentation.api.endpoints.users import router as users_router

api_router = APIRouter()

api_router.include_router(pages_router, tags=["Pages"])
api_router.include_router(auth_router, tags=["Auth"])
api_router.include_router(users_router, tags=["UserArticles"])
api_router.include_router(articles_router, tags=["Show"])
api_router.include_router(comments_router, tags=["Comments"])
api_router.include_router(admin_router, tags=["Admin"])
