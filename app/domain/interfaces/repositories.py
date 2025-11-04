from abc import ABC, abstractmethod


class IArticleRepository(ABC):
    @abstractmethod
    async def save(self, article):
        pass

    @abstractmethod
    async def last_article(self):
        pass

    @abstractmethod
    async def search_by_title(self, title):
        pass

    @abstractmethod
    async def log_in(self, dto):
        pass

    @abstractmethod
    async def sign_in(self, dto):
        pass