from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.application.dto.articleCreate_dto import ArticleCreateDTO
from app.application.services.article_manager import ArticleService
from app.domain.entities.user import UserEntity
from app.domain.logging import logger
from app.presentation.dependencies.articles_dependencies import get_article_manager
from app.presentation.dependencies.auth import get_current_user
from app.presentation.dependencies.parse_article import parse_article_form

router = APIRouter()

templates = Jinja2Templates('app/presentation/api/endpoints/templates')


@router.get("/articles/submit", response_class=HTMLResponse)
async def add(request: Request):
    return templates.TemplateResponse(
        name="submit_article.html",
        context={"request": request})


@router.post('/articles/submit/add')
async def create_article(
    request: Request,
    dto: ArticleCreateDTO = Depends(parse_article_form),
    manager: ArticleService = Depends(get_article_manager),
    user: UserEntity = Depends(get_current_user)
):
    logger.info(f'user : {user}')
    articles = await manager.add_article(dto, user.id)
    logger.info(f'articles : {articles}')
    return templates.TemplateResponse(
        name="search_results.html",
        context={"request": request, "articles": articles, "title": dto.title}
    )
