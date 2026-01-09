from app.application.dto.articleCreate_dto import ArticleCreateDTO
from app.domain.entities.article import ArticleEntity
from app.domain.interfaces.articleRepositories import IArticleRepository
from app.domain.interfaces.logic_repository import ILogicRepository


class ArticleService:
    def __init__(
            self,
            base_repository: IArticleRepository,
            logic_repository: ILogicRepository
            ):
        self.base_repository = base_repository
        self.logic_repository = logic_repository


    async def search_by_category(self, category: str) -> list[ArticleEntity] | None:
        return await self.base_repository.search_by_category(category)


    async def submit_article(self, dto: ArticleCreateDTO, user_id: int) -> ArticleEntity | None:
        check_limited = await self.logic_repository.check_limited(user_id)
        if not check_limited:
            return None
        mapping = {
            'title': dto.title,
            'content': dto.content,
            'user_id': user_id,
            'category': dto.category
        }
        return await self.base_repository.save(mapping, user_id)


    async def delete_article(self, article_id: int) -> dict:
        return await self.base_repository.delete(article_id)


    async def show_all_articles(self) -> list[ArticleEntity] | None:
        return await self.base_repository.all()


    async def search_by_title(self, title: str) -> list[ArticleEntity]:
        return await self.base_repository.search_by_title(title)


    async def list_user_articles(self, user_id: int) -> list[ArticleEntity]:
        return await self.base_repository.get_user_articles(user_id)


    async def get_by_id(self, user_id: int) -> ArticleEntity:
        return await self.base_repository.get_by_id(user_id)


    async def change_article(self, dto: ArticleCreateDTO, article_id: int) -> ArticleEntity:
        mapping = {
            'title': dto.title,
            'content': dto.content,
            'category': dto.category
        }
        return await self.base_repository.change(mapping, article_id)


    async def set_reaction(self, article_id: int, user_id: int, reaction: str):
        return await self.base_repository.set_reaction(article_id, user_id, reaction)

    async def liked_articles_by_user(self, user_id: int):
        result =  await self.base_repository.liked_articles_by_user(user_id)
        print(result)
        return result
