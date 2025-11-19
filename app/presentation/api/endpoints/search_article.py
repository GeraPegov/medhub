from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.application.services.article_service import ArticleService
from app.presentation.dependencies.articles_dependencies import get_article_manager

router = APIRouter()


templates = Jinja2Templates(directory="app/presentation/api/endpoints/templates")


@router.get('/articles/search', response_class=HTMLResponse)
async def search(
    request: Request,
    query: str = Query(..., min_length=2),
    manager: ArticleService = Depends(get_article_manager)
):
    articles = await manager.search_article(query)

    return templates.TemplateResponse(
        name="search.html",
        context={
            "request": request,
            "articles": articles,
            "title": query
            }
    )
