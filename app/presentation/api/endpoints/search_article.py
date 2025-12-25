from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.application.services.article_service import ArticleService
from app.domain.entities.user import UserEntity
from app.presentation.dependencies.articles_dependencies import get_article_manager


from app.presentation.dependencies.current_user import get_current_user

router = APIRouter()


templates = Jinja2Templates(directory="app/presentation/api/endpoints/templates/html")

@router.get('/articles/search')
async def search(
    request: Request
):
    
    return templates.TemplateResponse(
        'search.html',
        {
        'request': request
        }
    )

@router.get('/articles/search/title', response_class=HTMLResponse)
async def get_title(
    request: Request,
    query: str = Query(..., min_length=2),
    service: ArticleService = Depends(get_article_manager)
):
    articles = await service.search_by_title(query)

    return templates.TemplateResponse(
        name="search.html",
        context={
            "request": request,
            "articles": articles,
            "title": query,
            "auth": None
            }
    )

@router.get('/articles/search/category/{category}', response_class=HTMLResponse)
async def get_category(
    request: Request,
    category: str,
    service: ArticleService = Depends(get_article_manager),
    auth: UserEntity = Depends(get_current_user)
):
    articles = await service.search_by_category(category)

    return templates.TemplateResponse(
        name="search.html",
        context={
            "request": request,
            "articles": articles,
            "auth": auth
            }
    )
