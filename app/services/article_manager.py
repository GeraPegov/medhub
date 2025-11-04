from app.domain.entities import ArticleEntity
from app.domain.repositories import IArticleRepository
from app.models.pydantic import ArticleCreateDTO

class ArticleManager():
    def __init__(self, repository: IArticleRepository):
        self.repository = repository

    async def add_article(self, dto: ArticleCreateDTO):
        entity = ArticleEntity(
            author=dto.author,
            title=dto.title,
            article=dto.content
        )
        return await self.repository.save(entity)
    
    async def show_last_article(self):
        article = await self.repository.last_article()
        return article
    
    async def search_article(self, title):
        return await self.repository.search_by_title(title)
    
        