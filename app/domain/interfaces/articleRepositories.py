from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.article import ArticleEntity


class IArticleRepository(ABC):
    @abstractmethod
    def __init__(self, session: AsyncSession):
        pass

    @abstractmethod
    async def search_by_category(self, category: str) -> list[ArticleEntity] | None:
        pass

    @abstractmethod
    async def save(self, mapping: dict, author_id: int) -> ArticleEntity:
        pass

    @abstractmethod
    async def delete(self, article_id: int) -> dict:
        pass

    @abstractmethod
    async def get_by_id(self, article_id: int) -> ArticleEntity:
        pass

    @abstractmethod
    async def all(self) -> list[ArticleEntity] | None:
        pass

    @abstractmethod
    async def search_by_title(self, title: str) -> list[ArticleEntity]:
        pass

    @abstractmethod
    async def get_user_articles(self, user_id: int) -> list[ArticleEntity]:
        pass

    @abstractmethod
    async def change(self, mapping: dict, article_id: int) -> ArticleEntity:
        pass

    @abstractmethod
    async def set_reaction(self, user_id: int, article_id: int):
        pass

