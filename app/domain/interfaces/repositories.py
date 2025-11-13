from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.article import ArticleEntity


class IArticleRepository(ABC):
    @abstractmethod
    def __init__(self, session: AsyncSession):
        pass

    @abstractmethod
    async def save(self, entity: ArticleEntity) -> list[ArticleEntity]:
        pass

    @abstractmethod
    async def delete(self, article_id: int) -> dict:
        pass

    @abstractmethod
    async def show(self, article_id: int) -> ArticleEntity:
        pass

    @abstractmethod
    async def last_article(self) -> ArticleEntity:
        pass

    @abstractmethod
    async def search_by_title(self, title: str) -> list[ArticleEntity]:
        pass

    @abstractmethod
    async def get_user_articles(self, user_id: int) -> list[ArticleEntity]:
        pass

class ICommentRepository(ABC):

    @abstractmethod
    def __init__(self, session: AsyncSession):
        pass

    @abstractmethod
    async def show(self, article_id: int):
        pass

    @abstractmethod
    async def create(self, article_id: int, author_id: int):
        pass

    @abstractmethod
    async def delete(self, article_id: int, author_id: int):
        pass
