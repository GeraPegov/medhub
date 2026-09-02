from app.domain.entities.comment import CommentEntity
from app.domain.exceptions import NotFoundUserError
from app.domain.interfaces.comment_repository import ICommentRepository
from app.domain.interfaces.user_repository import IUserRepository


class CommentService:
    def __init__(
        self, comment_repository: ICommentRepository, user_repository: IUserRepository
    ):
        self.comment_repository = comment_repository
        self.user_repository = user_repository

    async def list_by_article_id(self, article_id: int) -> list[CommentEntity] | None:
        return await self.comment_repository.list_by_article_id(article_id)

    async def show_by_author(self, author_id: int) -> list[CommentEntity] | None:
        return await self.comment_repository.list_by_author(author_id)

    async def create(
        self, article_id: int, content: str, user_id: int
    ) -> CommentEntity:
        mapping = {"article_id": article_id, "content": content, "user_id": user_id}
        return await self.comment_repository.create(mapping)

    async def delete(self, comment_id: int, user_id: int) -> int:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundUserError
        return await self.comment_repository.delete(comment_id, user_id)
