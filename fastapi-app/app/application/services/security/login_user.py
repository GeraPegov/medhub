from app.domain.interfaces.auth_service import IAuthService
from app.domain.interfaces.user_repository import IUserRepository


class UserAuthenticationService:

    def __init__(
            self,
            auth_service: IAuthService,
            user_repo: IUserRepository
    ):
        self.user_repo = user_repo
        self.auth_service = auth_service


    async def execute(self, email: str, password: str) -> str | None:
        user = await self.user_repo.get_by_email(email)

        if not user:
            return None
        if not self.auth_service.verify_password(password, user.password_hash):
            return None

        token = self.auth_service.create_access_token(user.user_id)

        return token
