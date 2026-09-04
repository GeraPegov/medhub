from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.application.services.cache_service import CachedArticleService
from app.domain.entities.article import ArticleEntity


@pytest.fixture
def article() -> ArticleEntity:
    return ArticleEntity(
        article_id=7,
        title="Cached article",
        content="Detailed cached article content.",
        user_id=42,
        category="Research",
        unique_username="author",
        nickname="Author",
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
def logic_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def cached_article_service(
    cache_repository: AsyncMock,
    article_repository: AsyncMock,
    logic_repository: AsyncMock,
) -> CachedArticleService:
    return CachedArticleService(cache_repository, article_repository, logic_repository)


@pytest.mark.asyncio
async def test_get_article_from_cache(
    cached_article_service: CachedArticleService,
    cache_repository: AsyncMock,
    article_repository: AsyncMock,
    article: ArticleEntity,
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
    article: ArticleEntity,
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
    article: ArticleEntity,
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
async def test_delete_article_returns_cache_result(
    cached_article_service: CachedArticleService,
    cache_repository: AsyncMock,
    article: ArticleEntity,
):
    cache_repository.delete_article.return_value = 1

    result = await cached_article_service.delete_article(article.article_id)

    assert result == 1
    cache_repository.delete_article.assert_awaited_once_with(article.article_id)


@pytest.mark.asyncio
async def test_increment_view_counter_returns_cache_result(
    cached_article_service: CachedArticleService,
    cache_repository: AsyncMock,
    article: ArticleEntity,
):
    cache_repository.increment_view_counter.return_value = 6

    result = await cached_article_service.increment_view_counter(article.article_id)

    assert result == 6
    cache_repository.increment_view_counter.assert_awaited_once_with(article.article_id)


@pytest.mark.asyncio
async def test_update_views_counter_delegates_to_cache(
    cached_article_service: CachedArticleService,
    cache_repository: AsyncMock,
):
    await cached_article_service.update_views_counter()

    cache_repository.update_views_counter.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_add_reaction_returns_reaction_counts(
    cached_article_service: CachedArticleService,
    article_repository: AsyncMock,
    article: ArticleEntity,
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
