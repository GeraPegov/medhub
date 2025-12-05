from datetime import date, datetime

from redis.asyncio import Redis, RedisError

from app.domain.entities.article import ArticleEntity
from app.domain.entities.user import UserEntity
from app.domain.logging import logger
from app.infrastructure.database.repositories.article_repository import (
    ArticleRepository,
)
from app.infrastructure.database.repositories.user_repository import UserRepository


class CachedUser:
    def __init__(self, connection: Redis, session: UserRepository) -> bool:
        self.connection = connection
        self.session = session

    async def submit_user(
            self,
            id: int,
            email: str,
            username: str,
            nickname: str,
            password_hash: str):
        try:
            await self.connection.hmset(f'user:{id}', mapping={
                'email': email,
                'username': username,
                'nickname': nickname,
                'password_hash': password_hash
            })
            await self.connection.expire(f'user:{id}', 3600)
            return True
        except RedisError as e:
            logger.warning(f'Failed to cache user{id}: {e}')
            return False

    async def get_user(self, client_id) -> UserEntity | None:
            try:
                from_redis = await self.connection.hgetall(f'user:{client_id}')
                if from_redis:
                    return UserEntity(
                    id=client_id,
                    email=from_redis['email'],
                    username=from_redis['username'],
                    nickname=from_redis['nickname'],
                    password_hash=from_redis['password_hash']
                )
            except RedisError as e:
                logger.warning(f'Redis error when fetching user {client_id, {e}}')
            try:
                from_repo = await self.session.get_by_id(client_id)
                if from_repo:
                    logger.info('Success fetching user from redis')
                    await self.submit_user(
                            id=from_repo.id,
                            email=from_repo.email,
                            username=from_repo.username,
                            nickname=from_repo.nickname,
                            password_hash=from_repo.password_hash
                    )
                    return from_repo
                return None
            except Exception as e:
                logger.error(f'Database error when fetching user {client_id}: {e}')



class CachedArticle:
    def __init__(self, connection: Redis, session: ArticleRepository):
        self.connection = connection
        self.session = session

    async def submit_article(
            self,
            username: str,
            title: str,
            content: str,
            author_id: int,
            nickname: str | None = None,
            category: str | None = None,
            created_at: date | None = None,
            id: int | None = None
    ):
        try:
            await self.connection.hmset(f'article:{id}',
                {'username': username,
                'title': title,
                'content': content,
                'author_id': author_id,
                'nickname': nickname,
                'category': category,
                'created_at': created_at.isoformat() if created_at else None,
                'id': id}
            )
            await self.connection.expire(f'article:{id}', 3600)
            return True
        except RedisError as e:
            logger.warning(f'Failed to cache article {id}: {e}')
            return False

    async def get_article(self, article_id) -> ArticleEntity | None:
        try:
            from_redis = await self.connection.hgetall(f'article:{article_id}')
            if from_redis:
                logger.info('Success fetching article from redis')
                return ArticleEntity(
                    username=from_redis['username'],
                    title=from_redis['title'],
                    content=from_redis['content'],
                    author_id=from_redis['author_id'],
                    nickname=from_redis['nickname'],
                    category=from_redis['category'],
                    created_at=datetime.fromisoformat(from_redis['created_at']),
                    id=from_redis['id']
                )
        except RedisError as e:
            logger.warning(f'Redis error when fetching article {article_id}: {e}')
        try:
            from_repo = await self.session.get_by_id(article_id)
            if from_repo:
                await self.submit_article(
                    username=from_repo.username,
                    title=from_repo.title,
                    content=from_repo.content,
                    author_id=from_repo.author_id,
                    nickname=from_repo.nickname,
                    category=from_repo.category,
                    created_at=from_repo.created_at,
                    id=from_repo.id
                )
                return from_repo
            return None
        except Exception as e:
            logger.error(f'Database error when fetching article {article_id}: {e}')

