import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import UserEntity
from app.domain.exceptions import (
    NotFoundUserError,
    UserAlreadyExistsError,
    UsernameAlreadyExistsError,
)
from app.infrastructure.database.models.user import User
from app.infrastructure.database.repositories.user_repository import UserRepository


def user_data(**overrides) -> dict:
    data = {
        "email": "user@mail.com",
        "unique_username": "one_in_a_million",
        "nickname": "Any nickname",
        "password_hash": "hash",
    }
    data.update(overrides)
    return data


def assert_user_matches(
    user: UserEntity,
    *,
    user_id: int,
    email: str,
    unique_username: str,
    nickname: str,
    password_hash: str | None = None,
    subscriptions: list[str],
) -> None:
    assert user.user_id == user_id
    assert user.email == email
    assert user.unique_username == unique_username
    assert user.nickname == nickname
    assert user.password_hash == password_hash
    assert user.subscriptions == subscriptions


def assert_user_matches_model(user: UserEntity, model: User) -> None:
    assert_user_matches(
        user,
        user_id=model.id,
        email=model.email,
        unique_username=model.unique_username,
        nickname=model.nickname,
        password_hash=model.password_hash,
        subscriptions=list(model.subscriptions),
    )


@pytest.mark.asyncio
async def test_get_by_id_returns_complete_user_entity(
    db_session: AsyncSession, test_user1: User
):
    repository = UserRepository(db_session)

    user = await repository.get_by_id(test_user1.id)

    assert user is not None
    assert_user_matches_model(user, test_user1)


@pytest.mark.asyncio
async def test_get_by_id_returns_none_for_missing_id(
    db_session: AsyncSession, test_user1: User
):
    repository = UserRepository(db_session)

    user = await repository.get_by_id(999_999)

    assert user is None


@pytest.mark.asyncio
async def test_get_by_id_hides_deleted_user(db_session: AsyncSession, test_user1: User):
    repository = UserRepository(db_session)
    user_id = test_user1.id
    await repository.delete_profile(user_id)

    user = await repository.get_by_id(user_id)

    assert user is None


@pytest.mark.asyncio
async def test_get_by_email_returns_complete_user_entity(
    db_session: AsyncSession, test_user1: User
):
    repository = UserRepository(db_session)

    user = await repository.get_by_email(test_user1.email)

    assert user is not None
    assert_user_matches_model(user, test_user1)


@pytest.mark.asyncio
async def test_get_by_email_returns_none_for_missing_email(
    db_session: AsyncSession, test_user1: User
):
    repository = UserRepository(db_session)

    user = await repository.get_by_email("missing@example.com")

    assert user is None


@pytest.mark.asyncio
async def test_restore_deleted_by_email_restores_profile(
    db_session: AsyncSession, test_user1: User
):
    repository = UserRepository(db_session)
    user_id = test_user1.id
    email = test_user1.email
    await repository.delete_profile(user_id)
    assert await repository.get_by_id(user_id) is None

    restored = await repository.restore_deleted_by_email(email)

    assert restored is True
    user = await repository.get_by_id(user_id)
    assert user is not None
    assert_user_matches_model(user, test_user1)


@pytest.mark.asyncio
@pytest.mark.parametrize("email", ["test1@example.com", "missing@example.com"])
async def test_restore_deleted_by_email_returns_false_without_deleted_match(
    db_session: AsyncSession, test_user1: User, email: str
):
    repository = UserRepository(db_session)

    restored = await repository.restore_deleted_by_email(email)

    assert restored is False


@pytest.mark.asyncio
async def test_get_by_username_returns_complete_user_entity(
    db_session: AsyncSession, test_user1: User
):
    repository = UserRepository(db_session)

    user = await repository.get_by_username(test_user1.unique_username)

    assert user is not None
    assert_user_matches_model(user, test_user1)


@pytest.mark.asyncio
async def test_get_by_username_returns_none_for_missing_username(
    db_session: AsyncSession, test_user1: User
):
    repository = UserRepository(db_session)

    user = await repository.get_by_username("missing_username")

    assert user is None


@pytest.mark.asyncio
async def test_get_by_username_hides_deleted_user(
    db_session: AsyncSession, test_user1: User
):
    repository = UserRepository(db_session)
    username = test_user1.unique_username
    await repository.delete_profile(test_user1.id)

    user = await repository.get_by_username(username)

    assert user is None


@pytest.mark.asyncio
async def test_create_persists_complete_user(db_session: AsyncSession):
    repository = UserRepository(db_session)
    data = user_data()

    result = await repository.create(data)

    assert result is None
    user = await repository.get_by_email(data["email"])
    assert user is not None
    assert user.user_id is not None
    assert_user_matches(
        user,
        user_id=user.user_id,
        email=data["email"],
        unique_username=data["unique_username"],
        nickname=data["nickname"],
        password_hash=data["password_hash"],
        subscriptions=[],
    )


@pytest.mark.asyncio
async def test_create_raises_domain_error_for_duplicate_email(
    db_session: AsyncSession, test_user1: User
):
    repository = UserRepository(db_session)

    with pytest.raises(UserAlreadyExistsError):
        await repository.create(
            user_data(
                email=test_user1.email,
                unique_username="different_username",
            )
        )


@pytest.mark.asyncio
async def test_create_raises_domain_error_for_duplicate_username(
    db_session: AsyncSession, test_user1: User
):
    repository = UserRepository(db_session)

    with pytest.raises(UsernameAlreadyExistsError):
        await repository.create(
            user_data(
                email="different@example.com",
                unique_username=test_user1.unique_username,
            )
        )


@pytest.mark.asyncio
async def test_subscribe_adds_username_and_persists_complete_user(
    db_session: AsyncSession, test_user1: User, test_user2: User
):
    repository = UserRepository(db_session)
    original_subscriptions = list(test_user1.subscriptions)
    expected_subscriptions = [*original_subscriptions, test_user2.unique_username]

    user = await repository.subscribe(test_user1.id, test_user2.unique_username)

    assert user is not None
    assert_user_matches(
        user,
        user_id=test_user1.id,
        email=test_user1.email,
        unique_username=test_user1.unique_username,
        nickname=test_user1.nickname,
        password_hash=test_user1.password_hash,
        subscriptions=expected_subscriptions,
    )
    persisted = await repository.get_by_id(test_user1.id)
    assert persisted is not None
    assert persisted.subscriptions == expected_subscriptions


@pytest.mark.asyncio
async def test_subscribe_returns_none_without_adding_duplicate(
    db_session: AsyncSession, test_user1: User, test_user2: User
):
    repository = UserRepository(db_session)
    original_subscriptions = list(test_user1.subscriptions)
    await repository.subscribe(test_user1.id, test_user2.unique_username)

    result = await repository.subscribe(test_user1.id, test_user2.unique_username)

    assert result is None
    persisted = await repository.get_by_id(test_user1.id)
    assert persisted is not None
    assert persisted.subscriptions == [
        *original_subscriptions,
        test_user2.unique_username,
    ]
    assert persisted.subscriptions.count(test_user2.unique_username) == 1


@pytest.mark.asyncio
async def test_subscribe_raises_for_missing_subscriber(
    db_session: AsyncSession, test_user1: User
):
    repository = UserRepository(db_session)

    with pytest.raises(NotFoundUserError):
        await repository.subscribe(999_999, test_user1.unique_username)


@pytest.mark.asyncio
async def test_unsubscribe_removes_username_and_persists_complete_user(
    db_session: AsyncSession, test_user1: User, test_user2: User
):
    repository = UserRepository(db_session)
    original_subscriptions = list(test_user1.subscriptions)
    await repository.subscribe(test_user1.id, test_user2.unique_username)

    user = await repository.unsubscribe(test_user1.id, test_user2.unique_username)

    assert user is not None
    assert_user_matches(
        user,
        user_id=test_user1.id,
        email=test_user1.email,
        unique_username=test_user1.unique_username,
        nickname=test_user1.nickname,
        password_hash=test_user1.password_hash,
        subscriptions=original_subscriptions,
    )
    persisted = await repository.get_by_id(test_user1.id)
    assert persisted is not None
    assert persisted.subscriptions == original_subscriptions


@pytest.mark.asyncio
async def test_unsubscribe_returns_none_when_subscription_is_absent(
    db_session: AsyncSession, test_user1: User, test_user2: User
):
    repository = UserRepository(db_session)
    original_subscriptions = list(test_user1.subscriptions)

    result = await repository.unsubscribe(test_user1.id, test_user2.unique_username)

    assert result is None
    persisted = await repository.get_by_id(test_user1.id)
    assert persisted is not None
    assert persisted.subscriptions == original_subscriptions


@pytest.mark.asyncio
async def test_unsubscribe_raises_for_missing_subscriber(
    db_session: AsyncSession, test_user1: User
):
    repository = UserRepository(db_session)

    with pytest.raises(NotFoundUserError):
        await repository.unsubscribe(999_999, test_user1.unique_username)


@pytest.mark.asyncio
async def test_delete_profile_soft_deletes_user(
    db_session: AsyncSession, test_user1: User
):
    repository = UserRepository(db_session)
    user_id = test_user1.id
    username = test_user1.unique_username

    result = await repository.delete_profile(user_id)

    assert result is True
    is_deleted = (
        await db_session.execute(select(User.is_deleted).where(User.id == user_id))
    ).scalar_one()
    assert is_deleted is True
    assert await repository.get_by_id(user_id) is None
    assert await repository.get_by_username(username) is None


@pytest.mark.asyncio
async def test_delete_profile_raises_for_missing_user(db_session: AsyncSession):
    repository = UserRepository(db_session)

    with pytest.raises(NotFoundUserError):
        await repository.delete_profile(999_999)
