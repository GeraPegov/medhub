from unittest.mock import AsyncMock

import pytest

from app.application.services.comment_service import CommentService
from app.domain.exceptions import NotFoundUserError
from app.domain.interfaces.comment_repository import ICommentRepository
from app.domain.interfaces.user_repository import IUserRepository


@pytest.fixture
def comment_repository() -> AsyncMock:
    return AsyncMock(spec=ICommentRepository)


@pytest.fixture
def user_repository() -> AsyncMock:
    return AsyncMock(spec=IUserRepository)


@pytest.fixture
def service(
    comment_repository: AsyncMock, user_repository: AsyncMock
) -> CommentService:
    return CommentService(comment_repository, user_repository)


@pytest.mark.asyncio
@pytest.mark.parametrize("expected", [[], None])
async def test_show_by_author_delegates_to_list_by_author(
    service: CommentService, comment_repository: AsyncMock, expected
):
    comment_repository.list_by_author.return_value = expected

    result = await service.show_by_author(42)

    assert result is expected
    comment_repository.list_by_author.assert_awaited_once_with(42)


@pytest.mark.asyncio
async def test_delete_returns_article_id(
    service: CommentService,
    comment_repository: AsyncMock,
    user_repository: AsyncMock,
):
    user_repository.get_by_id.return_value = object()
    comment_repository.delete.return_value = 7

    result = await service.delete(comment_id=13, user_id=42)

    assert type(result) is int
    assert result == 7
    user_repository.get_by_id.assert_awaited_once_with(42)
    comment_repository.delete.assert_awaited_once_with(13, 42)


@pytest.mark.asyncio
async def test_delete_does_not_delete_when_user_is_missing(
    service: CommentService,
    comment_repository: AsyncMock,
    user_repository: AsyncMock,
):
    user_repository.get_by_id.return_value = None

    with pytest.raises(NotFoundUserError):
        await service.delete(comment_id=13, user_id=42)

    comment_repository.delete.assert_not_awaited()
