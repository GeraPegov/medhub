from fastapi import Cookie, Depends

from app.application.services.user_service import UserService
from app.domain.entities.user import UserEntity
from app.infrastructure.security.auth_service import AuthService
from app.presentation.dependencies.auth import (
    get_auth_service,
    get_user_service,
)


async def get_current_user(
        token = Cookie(None, alias='access_token'),
        auth_service: AuthService = Depends(get_auth_service),
        user_service: UserService = Depends(get_user_service)
) -> UserEntity | None:
    if not token:
        return None
    user_id = auth_service.verify_token(token)
    user = await user_service.get_by_id(user_id)
    if not user:
        return None
    return user

