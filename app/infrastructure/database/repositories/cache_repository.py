from datetime import date

from redis import Redis

from app.domain.entities.article import ArticleEntity
from app.domain.entities.user import UserEntity
from app.domain.logging import logger
from app.infrastructure.database.repositories.article_repository import (
    ArticleRepository,
)
from app.infrastructure.database.repositories.user_repository import UserRepository


class CachedUser:
    def __init__(self, connection: Redis, session: UserRepository):
        self.connection = connection
        self.session = session

    def submit_user(
            self,
            id: int,
            email: str,
            username:str,
            nickname: str,
            password_hash: str):
        self.connection.hmset(f'user:{id}', mapping={
            'email': email,
            'username': username,
            'nickname': nickname,
            'password_hash': password_hash
        })
        self.connection.expire(f'user:{id}', 3600)

    async def get_user(self, client_id) -> UserEntity:
            logger.info(f'start cache get_user {client_id}')
            from_redis = self.connection.hgetall(f'user:{client_id}')
            if from_redis:
                logger.info(f'if from redis accept {from_redis}')
                return UserEntity(
                id=client_id,
                email=from_redis['email'],
                username=from_redis['username'],
                nickname=from_redis['nickname'],
                password_hash=from_redis['password_hash']
            )
            from_repo = await self.session.get_by_id(client_id)
            logger.info(f'if from repo {from_repo.id}')
            self.submit_user(
                    id=from_repo.id,
                    email=from_repo.email,
                    username=from_repo.username,
                    nickname=from_repo.nickname,
                    password_hash=from_repo.password_hash
            )
            return from_repo


class CachedArticle:
    def __init__(self, connection: Redis, session: ArticleRepository):
        self.connection = connection
        self.session = session

    def submit_article(
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
        self.connection.hmset(f'article:{id}', mapping={
             'username': username,
             'title': title,
             'content': content,
             'author_id': author_id,
             'nickname': nickname,
             'category': category,
             'created_at': str(created_at),
             'id': id
        })

        self.connection.expire(f'article:{id}', 3600)

    async def get_article(self, article_id) -> list[ArticleEntity]:
        from_redis = self.connection.hgetall(f'article:{article_id}')
        logger.info(f'cahceservise input from cash : {from_redis}')
        if from_redis:
            return [ArticleEntity(
                username=from_redis['username'],
                title=from_redis['title'],
                content=from_redis['content'],
                author_id=from_redis['author_id'],
                nickname=from_redis['nickname'],
                category=from_redis['category'],
                created_at=from_redis['created_at'],
                id=from_redis['id']
            )]
        from_repo = await self.session.get_by_id(article_id)
        logger.info(f'cahceservise input from repo : {from_repo}')
        self.submit_article(
            username=from_repo[0].username,
            title=from_repo[0].title,
            content=from_repo[0].content,
            author_id=from_repo[0].author_id,
            nickname=from_repo[0].nickname,
            category=from_repo[0].category,
            created_at=from_repo[0].created_at,
            id=from_repo[0].id
        )

        return from_repo
