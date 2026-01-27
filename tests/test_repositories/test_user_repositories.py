import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.database.models.user import User


@pytest.mark.asyncio
async def test_create(db_session: AsyncSession):
    repo = UserRepository(db_session)
    user_data = {
        'email': 'asd@mail.ru',
        'unique_username': 'asd',
        'nickname': 'testuser',
        'password_hash': 'testpasswordasdf'
    }

    user = await repo.create(user_data)

    assert user.user_id is not None
    assert user.email == 'asd@mail.ru'
    assert user.nickname == 'testuser'
    assert user.password_hash == 'testpasswordasdf'


@pytest.mark.asyncio
async def test_get_by_id(db_session: AsyncSession, test_user1: User):
    repo = UserRepository(db_session)
    user = await repo.get_by_id(test_user1.id)

    assert user.user_id == test_user1.id


@pytest.mark.asyncio
async def test_get_by_email(db_session: AsyncSession, test_user1: User):
    repo = UserRepository(db_session)
    user = await repo.get_by_email(test_user1.email)

    assert user.email == test_user1.email


@pytest.mark.asyncio
async def test_get_by_username(db_session: AsyncSession, test_user1: User):
    repo = UserRepository(db_session)
    user = await repo.get_by_username(test_user1.unique_username)

    assert user.unique_username == test_user1.unique_username


@pytest.mark.asyncio
async def test_subscribe_and_unsubscribe(db_session: AsyncSession, test_user1: User, test_user2: User):
    repo = UserRepository(db_session)
    user = await repo.subscribe(
        subscribe_id=test_user1.id,
        author_unique_username=test_user2.unique_username
        )

    assert test_user2.unique_username in user.subscriptions

    user = await repo.unsubscribe(
        subscribe_id=test_user1.id,
        author_unique_username=test_user2.unique_username
        )

    assert test_user2.unique_username not in user.subscriptions


@pytest.mark.asyncio
async def test_to_entity(db_session: AsyncSession, test_user1: User):
    repo = UserRepository(db_session)

    user = await repo._to_entity(test_user1)

    assert user.email == test_user1.email
    assert user.password_hash == test_user1.password_hash
    assert user.unique_username == test_user1.unique_username
    assert user.nickname == test_user1.nickname
    assert user.subscriptions == test_user1.subscriptions
