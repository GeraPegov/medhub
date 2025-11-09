from app.application.dto.articleCreate_dto import ArticleCreateDTO
from app.domain.entities.article import ArticleEntity
from app.domain.interfaces.repositories import IArticleRepository


class ArticleManager:
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
        return await self.repository.last_article()

    async def search_article(self, title):
        return await self.repository.search_by_title(title)
