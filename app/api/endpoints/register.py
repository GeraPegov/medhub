from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from app.dependencies.parse_article import parse_register_form
from app.dependencies.depends_submit_article import get_article_manager
from app.services.article_manager import ArticleManager
from app.models.dto import ArticleRegisterDTO


router = APIRouter()

templates = Jinja2Templates('app/api/endpoints/templates')

@router.get('/register')
async def page_of_register(
    request: Request
):
    return templates.TemplateResponse(
        'register.html',
        {'request': request}
    )

@router.post('/auth/register')
async def main_register(
    request: Request,
    dto: ArticleRegisterDTO = Depends(parse_register_form),
    manager: ArticleManager = Depends(get_article_manager)
):
    await manager.log_in(dto)