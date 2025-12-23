from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.application.dto.articleCreate_dto import ArticleCreateDTO
from app.application.services.article_service import ArticleService
from app.domain.entities.user import UserEntity
from app.presentation.dependencies.articles_dependencies import get_article_manager
from app.presentation.dependencies.current_user import get_current_user
from app.presentation.dependencies.parse_article import parse_article_form

router = APIRouter()

templates = Jinja2Templates('app/presentation/api/endpoints/templates/html')


@router.get("/article/submit", response_class=HTMLResponse)
async def add(request: Request):
    return templates.TemplateResponse(
        name="submit_article.html",
        context={
            "request": request
            })


@router.post('/article/submit/add')
async def create_article(
    response: Response,
    dto: ArticleCreateDTO = Depends(parse_article_form),
    manager: ArticleService = Depends(get_article_manager),
    user: UserEntity = Depends(get_current_user)
):
    await manager.submit_article(dto, user.user_id)
    response = RedirectResponse(
        url=f'/user/profile/{user.unique_username}',
        status_code=303
    )

    return response
