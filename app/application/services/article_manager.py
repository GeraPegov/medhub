from app.application.dto.article_create_dto import ArticleCreateDTO
from app.domain.entities.article import ArticleEntity
from app.domain.interfaces.repositories import IArticleRepository


class ArticleService:
    def __init__(self, repository: IArticleRepository):
        self.repository = repository

    async def add_article(self, dto: ArticleCreateDTO, user_id: int, user_author: str) -> list[ArticleEntity]:
        entity = ArticleEntity(
            title=dto.title,
            content=dto.content,
            author_id=user_id,
            author=user_author
        )
        return await self.repository.save(entity)

    async def delete_article(self, article_id: int) -> dict:
        return await self.repository.delete(article_id)

    async def show_last_article(self) -> ArticleEntity:
        return await self.repository.last_article()

    async def search_article(self, title: str) -> list[ArticleEntity]:
        return await self.repository.search_by_title(title)

    async def list_user_articles(self, user_id: int) -> list[ArticleEntity]:
        return await self.repository.get_user_articles(user_id)

    async def show(self, article_id: int) -> ArticleEntity:
        return await self.repository.show(article_id)
