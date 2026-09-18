import aiohttp

from app.application.dto.article_create_dto import ArticleCreateDTO
from app.domain.entities.article import ArticleEntity
from app.domain.interfaces.article_repository import IArticleRepository
from app.domain.interfaces.logic_repository import ILogicRepository
from app.infrastructure.config import settings
from app.domain.exceptions import PublicationLimitError

ADMIN_API_URL = settings.ADMIN_API_URL

class ArticleService:
    def __init__(
        self,
        base_repository: IArticleRepository,
        logic_repository: ILogicRepository,
    ):
        self.base_repository = base_repository
        self.logic_repository = logic_repository

    async def search_by_category(self, category: str) -> list[ArticleEntity] | None:
        return await self.base_repository.search_by_category(category)

    async def submit_article(
        self, dto: ArticleCreateDTO, user_id: int
    ) -> int | None:
        try:
            async with aiohttp.request(
                "POST",
                f"{ADMIN_API_URL}/limiter/{user_id}/articles"
            ) as response:
                if response.status == 422:
                    raise PublicationLimitError
                elif response.status != 204:
                    await self.logic_repository.can_publish_article_today(user_id)

        except aiohttp.ClientConnectionError:
            await self.logic_repository.can_publish_article_today(user_id)

        mapping = {
                    "title": dto.title,
                    "content": dto.content,
                    "user_id": user_id,
                    "category": dto.category,
                    }
        article_id = await self.base_repository.save(mapping, user_id)
        return article_id


    async def delete_article(self, article_id: int, user_id: int) -> bool:
        return await self.base_repository.delete(article_id, user_id)

    async def show_all_articles(self) -> list[ArticleEntity] | None:
        return await self.base_repository.all()

    async def search_by_title(self, title: str) -> list[ArticleEntity]:
        return await self.base_repository.search_by_title(title)

    async def list_user_articles(self, user_id: int) -> list[ArticleEntity]:
        return await self.base_repository.get_user_articles(user_id)

    async def get_by_id(self, user_id: int) -> ArticleEntity:
        return await self.base_repository.get_by_id(user_id)

    async def change_article(
        self,
        dto: ArticleCreateDTO,
        article_id: int,
        user_id: int,
    ) -> ArticleEntity:
        mapping = {"title": dto.title, "content": dto.content, "category": dto.category}
        return await self.base_repository.change(mapping, article_id, user_id)

    async def liked_articles_by_user(self, user_id: int) -> list[ArticleEntity] | None:
        return await self.base_repository.liked_articles_by_user(user_id)
