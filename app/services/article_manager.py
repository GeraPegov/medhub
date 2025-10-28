from app.models.pydantic import ArticleModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.article_repository import ArticleRepository
from core.models.article import Article

class ArticleManager():
    def __init__(self, session: AsyncSession):
        self.repository = ArticleRepository(session)

    async def add_article(self, author, title, content):
        new_article = ArticleModel(author=author, title=title, content=content)
        article_for_db = Article(**new_article.model_dump())
        await self.repository.save(article_for_db)