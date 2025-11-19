# from abc import ABC, abstractmethod
# from app.domain.interfaces.articleRepositories import IArticleRepository
# from app.application.dto.articleCreate_dto import ArticleCreateDTO
# from app.domain.entities.article import ArticleEntity

# class ArticleService(ABC):
#     @abstractmethod
#     def __init__(self, repository: IArticleRepository):
#         pass

#     @abstractmethod
#     async def submit_article(self, dto: ArticleCreateDTO, user_id: int) -> list[ArticleEntity]:
#         pass

#     @abstractmethod
#     async def delete_article(self, article_id: int) -> dict:
#         pass

#     @abstractmethod
#     async def show_last_article(self) -> ArticleEntity:
#         pass

#     @abstractmethod
#     async def search_article(self, title: str) -> list[ArticleEntity]:
#         pass

#     @abstractmethod
#     async def list_user_articles(self, user_id: int) -> list[ArticleEntity]:
#         pass

#     @abstractmethod
#     async def only_article(self, article_id: int) -> ArticleEntity:
#         pass
