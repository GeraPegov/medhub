from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.dependencies.depends_submit_article import get_article_manager
from app.domain.logging import logger
from app.services.article_manager import ArticleManager

router = APIRouter()

templates = Jinja2Templates("app/api/endpoints/templates")

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
