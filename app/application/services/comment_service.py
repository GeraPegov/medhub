from app.domain.interfaces.comment_repositories import ICommentRepository
from app.domain.interfaces.user_repository import IUserRepository
from app.domain.entities. comment import CommentEntity


class CommentService:
    def __init__(self, comment_repository: ICommentRepository, user_repository: IUserRepository):
        self.comment_repository = comment_repository
        self.user_repository = user_repository

    async def show_by_article(self, article_id: int) -> list[CommentEntity] | None:
        return await self.comment_repository.show_by_article(article_id)

    async def show_by_author(self, author_id: int) -> list[CommentEntity] | None:
        return await self.comment_repository.show_by_author(author_id)

    async def create(self, article_id, content, user_id) -> CommentEntity:
        mapping = {
            'article_id': article_id,
            'content': content,
            'user_id': user_id
        }
        return await self.comment_repository.create(
            mapping
        )

    async def delete(self, comment_id, user_id) -> int | None:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None
        return await self.comment_repository.delete(comment_id)
