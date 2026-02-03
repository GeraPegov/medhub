from fastapi import Cookie, Depends

from app.application.services.cache_service import CachedServiceUser
from app.application.services.security.auth_service import AuthService
from app.domain.entities.user import UserEntity
from app.presentation.dependencies.auth import get_auth_service
from app.presentation.dependencies.cache import get_cache_user


async def get_current_user(
        token = Cookie(None, alias='access_token'),
        auth_service: AuthService = Depends(get_auth_service),
        user_service: CachedServiceUser = Depends(get_cache_user)
) -> UserEntity | None:
    if not token:
        return None
    user_id = auth_service.verify_token(token)
    user = await user_service.get_user(user_id)
    return user

