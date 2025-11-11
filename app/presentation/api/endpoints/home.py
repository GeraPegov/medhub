from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.application.services.article_manager import ArticleManager
from app.domain.entities.user import User
from app.presentation.dependencies.auth import get_current_user
from app.presentation.dependencies.depends_submit_article import get_article_manager

router = APIRouter()

templates = Jinja2Templates("app/presentation/api/endpoints/templates")


@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    manager: ArticleManager = Depends(get_article_manager),
    user: User = Depends(get_current_user)
    ):
    '''login это показ иконки авторизации для неавторизованных пользователей'''
    login = False
    if not user:
        login = True
    article = await manager.show_last_article()
    return templates.TemplateResponse(
        name='home.html', context={
            'login': login,
            'request': request,
            'articles': article
            })
