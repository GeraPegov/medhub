from app.services.article_manager import ArticleManager
from app.repositories.article_repository import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

def start_session(session: AsyncSession = Depends(get_db)):
    return ArticleManager(session)