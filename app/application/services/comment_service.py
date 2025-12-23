from app.domain.interfaces.commentRepositories import ICommentRepository
from app.domain.interfaces.user_repository import IUserRepository


class CommentService:
    def __init__(self, comment_repository: ICommentRepository, user_repository: IUserRepository):
        self.comment_repository = comment_repository
        self.user_repository = user_repository

    async def show_by_article(self, article_id: int):
        return await self.comment_repository.show_by_article(article_id)

    async def show_by_author(self, author_id: int):
        return await self.comment_repository.show_by_author(author_id)

    async def create(self, article_id, content, author_id):
        mapping = {
            'article_id': article_id,
            'content': content,
            'author_id': author_id
        }
        return await self.comment_repository.create(
            mapping
        )

    async def delete(self, comment_id, author_id):
        client = await self.user_repository.get_by_id(author_id)
        if not client:
            return 'warning: you are not holder of comment'
        return await self.comment_repository.delete(comment_id)
