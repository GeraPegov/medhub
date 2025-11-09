from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.application.dto.articleCreate_dto import ArticleCreateDTO
from app.application.services.article_manager import ArticleManager
from app.presentation.dependencies.depends_submit_article import get_article_manager
from app.presentation.dependencies.parse_article import parse_article_form

router = APIRouter()

templates = Jinja2Templates('app/api/endpoints/templates')


@router.get("/articles/submit", response_class=HTMLResponse)
async def add(request: Request):
    return templates.TemplateResponse(
        name="add_article.html",
        context={"request": request})


@router.post('/articles/submit/add')
async def create_article(
    request: Request,
    dto: ArticleCreateDTO = Depends(parse_article_form),
    manager: ArticleManager = Depends(get_article_manager)
):
    articles = await manager.add_article(dto)
    return templates.TemplateResponse(
        name="search_results.html",
        context={"request": request, "articles": articles, "title": dto.title}
    )
