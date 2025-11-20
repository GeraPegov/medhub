from redis import Redis

from app.domain.entities.user import UserEntity
from app.domain.logging import logger
from app.infrastructure.database.repositories.user_repository import UserRepository


class CachedRepository:
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
        self.connection.expire(f'user{id}', 3600)

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
