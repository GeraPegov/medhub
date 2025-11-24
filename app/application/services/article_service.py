from app.application.dto.articleCreate_dto import ArticleCreateDTO
from app.domain.entities.article import ArticleEntity
from app.domain.interfaces.articleRepositories import IArticleRepository


class ArticleService:
    def __init__(self, repository: IArticleRepository):
        self.repository = repository

    async def submit_article(self, dto: ArticleCreateDTO, user_id: int) -> list[ArticleEntity]:
        return await self.repository.save(dto, user_id)

    async def delete_article(self, article_id: int) -> dict:
        return await self.repository.delete(article_id)

    async def show_all_articles(self) -> list[ArticleEntity] | None:
        return await self.repository.all()

    async def search_article(self, title: str) -> list[ArticleEntity]:
        return await self.repository.search_by_title(title)

    async def list_user_articles(self, user_id: int) -> list[ArticleEntity]:
        return await self.repository.get_user_articles(user_id)

    async def only_article(self, article_id: int) -> list[ArticleEntity]:
        return await self.repository.show(article_id)
