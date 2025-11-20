from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.connection import get_db
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.security.auth_service import AuthService


def get_auth_service() -> AuthService:
    """Зависимость для сервиса авторизаци"""
    return AuthService()


def get_user_repository(session: AsyncSession = Depends(get_db)) -> UserRepository:
    """Зависиммость для репозитория пользователя"""
    return UserRepository(session)


