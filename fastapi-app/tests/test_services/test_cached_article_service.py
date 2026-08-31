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
def cache() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def article_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def logic_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(
    cache: AsyncMock,
    article_repository: AsyncMock,
    logic_repository: AsyncMock,
) -> CachedArticleService:
    return CachedArticleService(cache, article_repository, logic_repository)


def expected_cache_mapping(article: ArticleEntity) -> dict:
    return {
        "unique_username": article.unique_username,
        "title": article.title,
        "content": article.content,
        "user_id": article.user_id,
        "nickname": article.nickname,
        "created_at": article.created_at.timestamp(),
        "category": article.category,
        "article_id": article.article_id,
        "likes": article.likes,
        "dislikes": article.dislikes,
    }


@pytest.mark.asyncio
async def test_get_article_returns_cache_hit_without_querying_database(
    service: CachedArticleService,
    cache: AsyncMock,
    article_repository: AsyncMock,
    article: ArticleEntity,
):
    cache.get_cached_article.return_value = article

    result = await service.get_article(article.article_id)

    assert result is article
    cache.get_cached_article.assert_awaited_once_with(article.article_id)
    article_repository.get_by_id.assert_not_awaited()
    cache.set_cache.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_article_caches_database_result_after_cache_miss(
    service: CachedArticleService,
    cache: AsyncMock,
    article_repository: AsyncMock,
    article: ArticleEntity,
):
    cache.get_cached_article.return_value = None
    article_repository.get_by_id.return_value = article

    result = await service.get_article(article.article_id)

    assert result is article
    article_repository.get_by_id.assert_awaited_once_with(article.article_id)
    cache.set_cache.assert_awaited_once_with(
        "article",
        article.article_id,
        expected_cache_mapping(article),
        3600,
    )


@pytest.mark.asyncio
async def test_update_article_invalidates_then_rebuilds_cache(
    service: CachedArticleService, cache: AsyncMock, article: ArticleEntity
):
    result = await service.update_article(article)

    assert result is True
    cache.delete_article.assert_awaited_once_with(article.article_id)
    cache.set_cache.assert_awaited_once_with(
        "article",
        article.article_id,
        expected_cache_mapping(article),
        3600,
    )


@pytest.mark.asyncio
async def test_add_reaction_updates_repository_and_cache(
    service: CachedArticleService,
    article_repository: AsyncMock,
    article: ArticleEntity,
):
    article_repository.set_reaction.return_value = article
    service.update_article = AsyncMock()

    result = await service.add_reaction(
        user_id=42,
        article_id=article.article_id,
        reaction="like",
    )

    assert result == {"likes": article.likes, "dislikes": article.dislikes}
    article_repository.set_reaction.assert_awaited_once_with(
        article_id=article.article_id,
        user_id=42,
        reaction="like",
    )
    service.update_article.assert_awaited_once_with(article)


@pytest.mark.asyncio
async def test_cache_maintenance_methods_delegate_to_repository(
    service: CachedArticleService, cache: AsyncMock
):
    cache.delete_article.return_value = 1
    cache.increment_view_counter.return_value = 9

    assert await service.delete_article(7) == 1
    assert await service.increment_view_counter(7) == 9
    await service.update_views_counter()

    cache.delete_article.assert_awaited_once_with(7)
    cache.increment_view_counter.assert_awaited_once_with(7)
    cache.update_views_counter.assert_awaited_once_with()
