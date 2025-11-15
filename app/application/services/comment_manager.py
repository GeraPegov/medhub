from app.domain.interfaces.commentRepositories import ICommentRepository


class CommentService:
    def __init__(self, repository: ICommentRepository):
        self.repository = repository

    async def show(self, article_id: int):
        return await self.repository.show(article_id)

    async def create(self, article_id, content, author_id):
        return await self.repository.create(
            article_id=article_id,
            content=content,
            author_id=author_id
        )

    async def delete(self, article_id, author_id):
        return await self.repository.delete(article_id, author_id)
