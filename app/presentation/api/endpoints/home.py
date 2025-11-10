from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.application.services.article_manager import ArticleManager
from app.presentation.dependencies.depends_submit_article import get_article_manager

router = APIRouter()

templates = Jinja2Templates("app/presentation/api/endpoints/templates")

@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    manager: ArticleManager = Depends(get_article_manager)
    ):
    article = await manager.show_last_article()
    return templates.TemplateResponse(
        name='home.html', context={
            'request': request,
            'articles': article
            })
