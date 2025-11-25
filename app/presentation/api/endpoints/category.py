from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from app.application.services.article_service import ArticleService
from app.infrastructure.config import settings
from app.presentation.dependencies.articles_dependencies import get_article_manager

router = APIRouter()

templates = Jinja2Templates("app/presentation/api/endpoints/templates/html")

@router.get('/articles/categories')
async def category(
    request: Request
):
    categories = settings.CATEGORIES.split(',')
    biochemystry = settings.BIOCHEMISTRY.split(',')
    return templates.TemplateResponse(
        'category.html',
        {'request': request,
        'categories': categories,
        'biochemistry': biochemystry
        }
    )

@router.get('/articles/category/{name}')
async def name(
    request: Request,
    name: str,
    manager: ArticleService = Depends(get_article_manager)
):
    articles = await manager.search_by_category(name)

    return templates.TemplateResponse(
        'home.html',
        {'request': request,
         'articles': articles
         }
    )
