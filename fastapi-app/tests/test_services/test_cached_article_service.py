from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.application.services.cache_service import CachedArticleService
from app.domain.read_models import ArticleReadModel


@pytest.fixture
def article() -> ArticleReadModel:
    return ArticleReadModel(
        article_id=7,
        title="Cached article",
        content="Detailed cached article content.",
        user_id=42,
        category="Research",
        author_username="author",
        author_nickname="Author",
        likes=5,
        dislikes=2,
        created_at=datetime(2026, 8, 31, 12, 0),
    )


@pytest.fixture
def cache_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def article_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def cached_article_service(
    cache_repository: AsyncMock,
    article_repository: AsyncMock,
) -> CachedArticleService:
    return CachedArticleService(cache_repository, article_repository)


@pytest.mark.asyncio
async def test_get_article_from_cache(
    cached_article_service: CachedArticleService,
    cache_repository: AsyncMock,
    article_repository: AsyncMock,
    article: ArticleReadModel,
):
    cache_repository.get_cached_article.return_value = article
    result = await cached_article_service.get_article(article.article_id)

    assert result == article

    cache_repository.get_cached_article.assert_awaited_once_with(article.article_id)
    article_repository.get_by_id.assert_not_awaited()
    cache_repository.set_cache.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_article_from_repository(
    cached_article_service: CachedArticleService,
    cache_repository: AsyncMock,
    article_repository: AsyncMock,
    article: ArticleReadModel,
):
    cache_repository.get_cached_article.return_value = None
    article_repository.get_by_id.return_value = article

    result = await cached_article_service.get_article(article.article_id)
    assert result == article
    data = {
        "unique_username": "author",
        "title": "Cached article",
        "content": "Detailed cached article content.",
        "user_id": 42,
        "nickname": "Author",
        "category": "Research",
        "created_at": datetime(2026, 8, 31, 12, 0).timestamp(),
        "article_id": 7,
        "likes": 5,
        "dislikes": 2,
    }

    cache_repository.get_cached_article.assert_awaited_once_with(article.article_id)
    article_repository.get_by_id.assert_awaited_once_with(article.article_id)
    cache_repository.set_cache.assert_awaited_once_with(
        "article", article.article_id, data, 3600
    )


@pytest.mark.asyncio
async def test_update_article_refreshes_cache(
    cached_article_service: CachedArticleService,
    cache_repository: AsyncMock,
    article: ArticleReadModel,
):
    cache_repository.delete_article.return_value = None

    result = await cached_article_service.update_article(article)

    assert result is None
    data = {
        "unique_username": "author",
        "title": "Cached article",
        "content": "Detailed cached article content.",
        "user_id": 42,
        "nickname": "Author",
        "category": "Research",
        "created_at": datetime(2026, 8, 31, 12, 0).timestamp(),
        "article_id": 7,
        "likes": 5,
        "dislikes": 2,
    }

    cache_repository.delete_article.assert_awaited_once_with(article.article_id)
    cache_repository.set_cache.assert_awaited_once_with(
        "article", article.article_id, data, 3600
    )


@pytest.mark.asyncio
async def test_delete_article_deletes_database_and_invalidates_article_and_comments(
    cached_article_service: CachedArticleService,
    cache_repository: AsyncMock,
    article_repository: AsyncMock,
    article: ArticleReadModel,
):
    result = await cached_article_service.delete_article(
        article.article_id, article.user_id
    )

    assert result is None
    article_repository.delete.assert_awaited_once_with(
        article.article_id, article.user_id
    )
    cache_repository.delete_article.assert_awaited_once_with(article.article_id)
    cache_repository.delete_comments.assert_awaited_once_with(article.article_id)


@pytest.mark.asyncio
async def test_invalidate_article_only_deletes_cache(
    cached_article_service: CachedArticleService,
    cache_repository: AsyncMock,
    article_repository: AsyncMock,
    article: ArticleReadModel,
):
    await cached_article_service.invalidate_article(article.article_id)

    article_repository.delete.assert_not_awaited()
    cache_repository.delete_article.assert_awaited_once_with(article.article_id)
    cache_repository.delete_comments.assert_awaited_once_with(article.article_id)


@pytest.mark.asyncio
async def test_add_reaction_returns_reaction_counts(
    cached_article_service: CachedArticleService,
    article_repository: AsyncMock,
    article: ArticleReadModel,
):
    update_article = AsyncMock()
    cached_article_service.update_article = update_article
    article_repository.set_reaction.return_value = article

    result = await cached_article_service.add_reaction(1, article.article_id, "like")

    assert result == {"likes": article.likes, "dislikes": article.dislikes}
    article_repository.set_reaction.assert_awaited_once_with(
        article_id=article.article_id,
        user_id=1,
        reaction="like",
    )
    update_article.assert_awaited_once_with(article)
