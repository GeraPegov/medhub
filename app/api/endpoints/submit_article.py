from fastapi import APIRouter, Form, Depends
from app.services.article_manager import ArticleManager
from app.dependencies.depends_submit_article import start_session

router = APIRouter()

@router.post('/submit-article')
async def add_article_in_db(
    author: str = Form(),
    title: str = Form(),
    content: str = Form(),
    manager: ArticleManager = Depends(start_session),
):
    await manager.add_article(author, title, content)
    return 'thank you'
    