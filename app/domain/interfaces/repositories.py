from abc import ABC, abstractmethod


class IArticleRepository(ABC):
    @abstractmethod
    async def save_db(self, content):
        pass

    @abstractmethod
    async def last_article_db(self):
        pass

    @abstractmethod
    async def search_by_title_db(self, title: str):
        pass

    @abstractmethod
    async def list_user_articles_db(self, id: int):
        pass

    @abstractmethod
    async def delete_article_db(self, id: int):
        pass
