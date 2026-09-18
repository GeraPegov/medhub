import aiohttp

from app.domain.entities.comment import CommentEntity
from app.domain.exceptions import NotFoundUserError
from app.domain.interfaces.comment_repository import ICommentRepository
from app.domain.interfaces.logic_repository import ILogicRepository
from app.domain.interfaces.user_repository import IUserRepository
from app.infrastructure.config import settings
from app.domain.exceptions import PublicationLimitError

ADMIN_API_URL = settings.ADMIN_API_URL

class CommentService:
    def __init__(
        self, comment_repository: ICommentRepository, user_repository: IUserRepository, logic_repository: ILogicRepository
    ):
        self.comment_repository = comment_repository
        self.user_repository = user_repository
        self.logic_repository = logic_repository

    async def list_by_article_id(self, article_id: int) -> list[CommentEntity] | None:
        return await self.comment_repository.list_by_article_id(article_id)

    async def show_by_author(self, author_id: int) -> list[CommentEntity] | None:
        return await self.comment_repository.list_by_author(author_id)

    async def create(
        self, article_id: int, content: str, user_id: int
    ) -> int:
        try:
            async with aiohttp.request(
                "POST",
                f"{ADMIN_API_URL}/limiter/{user_id}/{article_id}/comments"
            ) as response:
                if response.status == 422:
                    raise PublicationLimitError
                elif response.status != 204:
                    await self.logic_repository.can_publish_comment_today(user_id, article_id)
        except aiohttp.ClientConnectionError:
            await self.logic_repository.can_publish_comment_today(user_id, article_id)

        mapping = {"article_id": article_id, "content": content, "user_id": user_id}
        return await self.comment_repository.create(mapping)

    async def delete(self, comment_id: int, user_id: int) -> int:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundUserError
        return await self.comment_repository.delete(comment_id, user_id)
