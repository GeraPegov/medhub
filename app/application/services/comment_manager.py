from app.domain.interfaces.commentRepositories import ICommentRepository
from app.domain.interfaces.user_repository import IUserRepository


class CommentService:
    def __init__(self, comment_repository: ICommentRepository, user_repository: IUserRepository):
        self.comment_repository = comment_repository
        self.user_repository = user_repository

    async def show_comment(self, article_id: int):
        return await self.comment_repository.show(article_id)

    async def create_comment(self, article_id, content, author_id):
        return await self.comment_repository.create(
            article_id=article_id,
            content=content,
            author_id=author_id
        )

    async def delete_comment(self, comment_id, author_id):
        client = await self.user_repository.get_by_id(author_id)
        if not client:
            return 'warning: you are not holder of comment'
        return await self.comment_repository.delete(comment_id)
