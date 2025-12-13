import json
from datetime import date, datetime

from redis.asyncio import Redis, RedisError

from app.domain.entities.article import ArticleEntity
from app.domain.entities.user import UserEntity
from app.domain.logging import logger
from app.infrastructure.database.repositories.article_repository import (
    ArticleRepository,
)
from app.infrastructure.database.repositories.user_repository import UserRepository


class CachedAuth:
    def __init__(self, connection: Redis, session: UserRepository):
        self.connection = connection
        self.session = session

    async def submit_auth(
            self,
            user_id: int,
            email: str,
            unique_username: str,
            nickname: str,
            subscriptions: list[str]
    ):
        try:
            await self.connection.hmset(f'user:{user_id}', mapping={
                'email': email,
                'nickname': nickname,
                'unique_username': unique_username,
                'subscriptions': json.dumps(list(subscriptions))
            })
            await self.connection.expire(f'user:{id}')
            return True
        except RedisError as e:
            logger.warning(f'Failed to cache user{unique_username}: {e}')
            return False
        
    async def get_auth(self, user_id: int) -> UserEntity | None:
        try:
            from_redis = await self.connection.hgetall(f'user:{user_id}')
            if from_redis:
                        return UserEntity(
                        id=user_id,
                        email=from_redis['email'],
                        unique_username=from_redis['unique_username'],
                        nickname=from_redis['nickname'],
                        subscriptions=json.loads(from_redis['subscriptions'])
                    )
        except RedisError as e:
            logger.warning(f'Redis error when fetching user {user_id, {e}}')
        try:
            from_repo = await self.session.get_by_id(user_id)
            if from_repo:
                await self.submit_auth(
                        id=from_repo.id,
                        email=from_repo.email,
                        unique_username=from_repo.unique_username,
                        nickname=from_repo.nickname,
                        subscriptions=from_repo.subscriptions
                )
                return from_repo
            return None
        except Exception as e:
            logger.error(f'Database error when fetching user {user_id}: {e}')



class CachedUser:
    def __init__(self, connection: Redis, session: UserRepository) -> bool:
        self.connection = connection
        self.session = session

    async def submit_user(
            self,
            id: int,
            email: str,
            unique_username: str,
            nickname: str,
            subscriptions: list[str]
            ):
        try:
            await self.connection.hmset(f'user:{unique_username}', mapping={
                'email': email,
                'id': id,
                'nickname': nickname,
                'subscriptions': json.dumps(list(subscriptions))
            })
            await self.connection.expire(f'user:{unique_username}', 3600)
            return True
        except RedisError as e:
            logger.warning(f'Failed to cache user{unique_username}: {e}')
            return False

    async def get_user(self, unique_username: str) -> UserEntity | None:
            try:
                from_redis = await self.connection.hgetall(f'user:{unique_username}')
                if from_redis:
                    return UserEntity(
                    id=int(from_redis['id']),
                    email=from_redis['email'],
                    unique_username=unique_username,
                    nickname=from_redis['nickname'],
                    subscriptions=json.loads(from_redis['subscriptions'])
                )
            except RedisError as e:
                logger.warning(f'Redis error when fetching user {unique_username, {e}}')
            try:
                from_repo = await self.session.get_by_username(unique_username)
                if from_repo:
                    logger.info('Success fetching user from redis')
                    await self.submit_user(
                            id=from_repo.id,
                            email=from_repo.email,
                            unique_username=from_repo.unique_username,
                            nickname=from_repo.nickname,
                            subscriptions=from_repo.subscriptions
                    )
                    return from_repo
                return None
            except Exception as e:
                logger.error(f'Database error when fetching user {unique_username}: {e}')



class CachedArticle:
    def __init__(self, connection: Redis, session: ArticleRepository):
        self.connection = connection
        self.session = session

    async def submit_article(
            self,
            unique_username: str,
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
                {'unique_username': unique_username,
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
                    unique_username=from_redis['unique_username'],
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
                    unique_username=from_repo.unique_username,
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

