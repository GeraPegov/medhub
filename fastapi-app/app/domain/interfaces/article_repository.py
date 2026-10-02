from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.read_models import ArticleReadModel


class IArticleRepository(ABC):
    @abstractmethod
    def __init__(self, session: AsyncSession):
        pass

    @abstractmethod
    async def search_by_category(self, category: str) -> list[ArticleReadModel] | None:
        pass

    @abstractmethod
    async def save(self, mapping: dict, author_id: int) -> int:
        pass

    @abstractmethod
    async def delete(self, article_id: int, user_id: int) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, article_id: int) -> ArticleReadModel:
        pass

    @abstractmethod
    async def all(self) -> list[ArticleReadModel] | None:
        pass

    @abstractmethod
    async def search_by_title(self, title: str) -> list[ArticleReadModel] | None:
        pass

    @abstractmethod
    async def get_user_articles(self, user_id: int) -> list[ArticleReadModel] | None:
        pass

    @abstractmethod
    async def change(
        self,
        mapping: dict,
        article_id: int,
        user_id: int,
    ) -> ArticleReadModel:
        pass

    @abstractmethod
    async def set_reaction(
        self, article_id: int, user_id: int, reaction: str
    ) -> ArticleReadModel:
        pass

    @abstractmethod
    async def liked_articles_by_user(
        self, user_id: int
    ) -> list[ArticleReadModel] | None:
        pass
