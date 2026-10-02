from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.application.services.cache_service import CachedCommentService
from app.domain.read_models import CommentReadModel


@pytest.fixture
def comment() -> CommentReadModel:
    return CommentReadModel(
        id=13,
        user_id=42,
        article_id=7,
        content="Cached comment",
        created_at=datetime(2026, 9, 30, 12, 0),
        author_username="author",
        author_nickname="Author",
    )


@pytest.fixture
def cache_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def comment_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def cached_comment_service(
    cache_repository: AsyncMock,
    comment_repository: AsyncMock,
) -> CachedCommentService:
    return CachedCommentService(cache_repository, comment_repository)


@pytest.mark.asyncio
async def test_get_comments_returns_cached_read_models_without_database_query(
    cached_comment_service: CachedCommentService,
    cache_repository: AsyncMock,
    comment_repository: AsyncMock,
    comment: CommentReadModel,
):
    cache_repository.get_cached_comments_for_article.return_value = [comment]

    result = await cached_comment_service.get_comments_for_article(comment.article_id)

    assert result == [comment]
    comment_repository.list_by_article_id.assert_not_awaited()
    cache_repository.set_cache.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_comments_caches_database_read_models(
    cached_comment_service: CachedCommentService,
    cache_repository: AsyncMock,
    comment_repository: AsyncMock,
    comment: CommentReadModel,
):
    cache_repository.get_cached_comments_for_article.return_value = None
    comment_repository.list_by_article_id.return_value = [comment]

    result = await cached_comment_service.get_comments_for_article(comment.article_id)

    assert result == [comment]
    cache_repository.set_cache.assert_awaited_once_with(
        "comments",
        comment.article_id,
        [
            {
                "id": comment.id,
                "content": comment.content,
                "user_id": comment.user_id,
                "author_nickname": comment.author_nickname,
                "author_username": comment.author_username,
                "created_at": comment.created_at.timestamp(),
                "article_id": comment.article_id,
            }
        ],
        3600,
    )


@pytest.mark.asyncio
async def test_invalidate_comments_only_deletes_cache_key(
    cached_comment_service: CachedCommentService,
    cache_repository: AsyncMock,
    comment_repository: AsyncMock,
):
    await cached_comment_service.invalidate_comments(7)

    cache_repository.delete_comments.assert_awaited_once_with(7)
    comment_repository.delete.assert_not_awaited()
