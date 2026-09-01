
from unittest.mock import AsyncMock
import pytest
from app.application.services.user_service import UserService
from app.domain.entities.user import UserEntity

@pytest.fixture
def user_repository() -> AsyncMock:
    return AsyncMock()

@pytest.fixture
async def service(user_repository: AsyncMock) -> UserService:
    return UserService(user_repository)

@pytest.mark.asyncio
async def test_create_user_complete_create_mapping(
    service: UserService,
    user_repository: AsyncMock
    ):
    mapping = {
        "password_hash": "example hash",
        "unique_username": "username",
        "email": "example@mail.com",
        "nickname": "nickname",
    }
    user_repository.create.return_value = None
    result = await service.create(
        email="example@mail.com",
        password_hash="example hash",
        username="username",
        nickname="nickname"
    )
    assert result is None

    user_repository.create.assert_awaited_once_with(
        mapping
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('service_method', 'repository_method', 'arguments', 'expected'),
    [
        ("get_by_id", "get_by_id", (1,), "user"),
        ("get_by_email", "get_by_email", ("example@mail.com",), "user"),
        ("get_by_username", "get_by_username", ("example username",), "user"),
        ("subscribe", "subscribe", (1, "example username"), "user"),
        ("unsubscribe", "unsubscribe", (1, "example username"), "user"),
        ("delete_profile", "delete_profile", (1,), True)
    ]
)
async def test_query_methods_delegate_without_changing_arguments(
    service: UserService,
    user_repository: AsyncMock,
    service_method: str,
    repository_method: str,
    arguments: tuple,
    expected
):
    repository_call = getattr(user_repository, repository_method)
    repository_call.return_value = expected

    result = await getattr(service, service_method)(*arguments)

    assert result == expected

    repository_call.assert_awaited_once_with(
        *arguments
    )
