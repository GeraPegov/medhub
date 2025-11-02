from fastapi import APIRouter, Depends, Query, Request
from app.dependencies.depends_submit_article import start_session
from app.services.article_manager import ArticleManager
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="app/api/endpoints/templates")

@router.get('/articles/search', response_class=HTMLResponse)
async def search(
    request: Request,
    query: str = Query(...),
    manager: ArticleManager = Depends(start_session)
):
    articles = await manager.search_article(query)
    
    return templates.TemplateResponse(
        name="search_results.html",
        context={"request": request, "articles": articles, "title": query}
    )