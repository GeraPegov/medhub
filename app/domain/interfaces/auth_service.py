from abc import ABC, abstractmethod


class IAuthService(ABC):

    @abstractmethod
    def create_access_token(self, user_id: int) -> str:
        pass

    @abstractmethod
    async def verify_token(self, token: str) -> int:
        '''Возвращает user_id из токена'''
        pass

    @abstractmethod
    def hash_password(self, password: str) -> str:
        pass

    @abstractmethod
    async def verify_password(self, plain_password: str, hashed: str) -> bool:
        pass

