from passlib.context import CryptContext

from app.domain.logging import logger


class PasswordHasher:
    '''Хеширование паролей'''

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

    def hash(self, password: str) -> str:
        logger.info(f'create hash = {password}')
        return self.pwd_context.hash(password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
