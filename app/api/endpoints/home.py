from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.dependencies.depends_submit_article import start_session
from app.services.article_manager import ArticleManager



router = APIRouter()

templates = Jinja2Templates("app/api/endpoints/templates")


@router.get("/add-article", response_class=HTMLResponse)
async def add(request: Request):
    return templates.TemplateResponse(name="add_article.html", context={"request": request})

@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    manager: ArticleManager = Depends(start_session)
    ):
    article = await manager.show_last_article()
    return templates.TemplateResponse(
        name='home.html', context={
            'request': request,
            'articles': article
            })
