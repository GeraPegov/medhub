import pytest
from redis.asyncio import Redis

from app.infrastructure.database.models.article import Article
from app.infrastructure.database.models.user import User
from app.infrastructure.database.repositories.cache_repository import CachedRepository


def article_cache_mapping(article: Article, author: User) -> dict:
    return {
        "unique_username": author.unique_username,
        "title": article.title,
        "content": article.content,
        "user_id": article.user_id,
        "nickname": author.nickname,
        "created_at": article.created_at.timestamp(),
        "category": article.category,
        "article_id": article.id,
        "likes": article.like,
        "dislikes": article.dislike,
    }


@pytest.mark.asyncio
async def test_article_cache_round_trip_preserves_complete_entity(
    db_redis: Redis, test_article: Article, test_user1: User
):
    repository = CachedRepository(db_redis)
    mapping = article_cache_mapping(test_article, test_user1)

    result = await repository.set_cache(
        prefix="article",
        key=test_article.id,
        mapping=mapping,
        ttl=60,
    )
    cached = await repository.get_cached_article(test_article.id)

    assert result is True
    assert cached is not None
    assert cached.article_id == test_article.id
    assert cached.user_id == test_article.user_id
    assert cached.unique_username == test_user1.unique_username
    assert cached.nickname == test_user1.nickname
    assert cached.title == test_article.title
    assert cached.content == test_article.content
    assert cached.category == test_article.category
    assert cached.created_at == test_article.created_at
    assert cached.likes == test_article.like
    assert cached.dislikes == test_article.dislike
    assert 0 < await db_redis.ttl(f"article:{test_article.id}") <= 60


@pytest.mark.asyncio
async def test_get_cached_article_returns_none_for_missing_key(db_redis: Redis):
    repository = CachedRepository(db_redis)

    assert await repository.get_cached_article(999_999) is None


@pytest.mark.asyncio
async def test_delete_article_removes_cached_value(
    db_redis: Redis, test_article: Article, test_user1: User
):
    repository = CachedRepository(db_redis)
    await repository.set_cache(
        prefix="article",
        key=test_article.id,
        mapping=article_cache_mapping(test_article, test_user1),
    )

    deleted_count = await repository.delete_article(test_article.id)

    assert deleted_count == 1
    assert await repository.get_cached_article(test_article.id) is None


@pytest.mark.asyncio
async def test_increment_view_counter_is_atomic(db_redis: Redis):
    repository = CachedRepository(db_redis)

    first = await repository.increment_view_counter(7)
    second = await repository.increment_view_counter(7)

    assert first == 1
    assert second == 2
    assert await db_redis.get("article_counter:7") == "2"
