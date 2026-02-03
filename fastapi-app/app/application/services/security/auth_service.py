from app.application.services.security.jwt_handler import JWTHandler
from app.application.services.security.password_hasher import PasswordHasher
from app.domain.interfaces.auth_service import IAuthService


class AuthService(IAuthService):

    def __init__(self):
        self.jwt_handler = JWTHandler()
        self.password_hasher = PasswordHasher()

    def create_access_token(self, user_id: int) -> str:
        return self.jwt_handler.create_token(user_id)

    def verify_token(self, token: str) -> int | None:
        return self.jwt_handler.verify_token(token)

    def hash_password(self, password: str) -> str:
        return self.password_hasher.hash(password)

    def verify_password(self, plain_password: str, hashed: str) -> bool:
        return self.password_hasher.verify(plain_password, hashed)

