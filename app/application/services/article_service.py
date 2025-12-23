from app.application.dto.articleCreate_dto import ArticleCreateDTO
from app.domain.entities.article import ArticleEntity
from app.domain.interfaces.articleRepositories import IArticleRepository


class ArticleService:
    def __init__(self, repository: IArticleRepository):
        self.repository = repository

    async def search_by_category(self, category: str) -> list[ArticleEntity] | None:
        return await self.repository.search_by_category(category)

    async def submit_article(self, dto: ArticleCreateDTO, author_id: int) -> ArticleEntity:
        mapping = {
            'title': dto.title,
            'content': dto.content,
            'author_id': author_id,
            'category': dto.category
        }
        return await self.repository.save(mapping, author_id)

    async def delete_article(self, article_id: int) -> dict:
        return await self.repository.delete(article_id)

    async def show_all_articles(self) -> list[ArticleEntity] | None:
        return await self.repository.all()

    async def search_article(self, title: str) -> list[ArticleEntity]:
        return await self.repository.search_by_title(title)

    async def list_user_articles(self, user_id: int) -> list[ArticleEntity]:
        return await self.repository.get_user_articles(user_id)

    async def get_by_id(self, article_id: int) -> list[ArticleEntity]:
        return await self.repository.get_by_id(article_id)

    async def change_article(self, dto: ArticleCreateDTO, article_id: int) -> list[ArticleEntity]:
        mapping = {
            'title': dto.title,
            'content': dto.content,
            'category': dto.category
        }
        return await self.repository.change(mapping, article_id)
