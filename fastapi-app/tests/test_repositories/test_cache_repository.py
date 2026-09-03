from datetime import datetime
import json

import pytest
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import UserEntity
from app.domain.entities.article import ArticleEntity
from app.infrastructure.database.models.user import User
from app.infrastructure.database.models.article import Article

from app.infrastructure.database.repositories.cache_repository import CachedRepository
from app.infrastructure.database.repositories.article_repository import ArticleRepository
from app.infrastructure.database.repositories.user_repository import UserRepository

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
    assert json.dumps(user.subscriptions) == subscriptions

def assert_article_matches(
    article: ArticleEntity,
    *,
    article_id: int,
    author: User,
    title: str,
    content: str,
    category: str,
) -> None:
    assert article.article_id == article_id
    assert article.user_id == author.id
    assert article.unique_username == author.unique_username
    assert article.nickname == author.nickname
    assert article.title == title
    assert article.content == content
    assert article.category == category
    assert article.likes == 0
    assert article.dislikes == 0
    assert article.created_at is not None


def data_cache_user(
        user_id: int,
        **overrides
        ):
    data = {
        "user_id": user_id,
        "email": "any@example.com",
        "unique_username": "any username",
        "nickname": "any nickname",
        "subscriptions": json.dumps(['any subscribe']),
    }
    data.update(overrides)
    return data


def data_cache_article(
        article_id: int,
        **overrides
        ):
    data = {
            "unique_username": "any username",
            "title": "any title",
            "content": "any content",
            "user_id": 1,
            "nickname": "any nickname",
            "created_at": (datetime.now()).timestamp(),
            "category": "any category",
            "article_id": article_id,
            "likes": 2,
            "dislikes": 3,
        }
    data.update(overrides)
    return data


@pytest.mark.asyncio
async def test_create_cash_user_return_complete_none(db_redis: Redis, test_user1: User):
    repository = CachedRepository(db_redis)
    data_cache = data_cache_user(test_user1.id)
    cache_result = await repository.set_cache(
        record_selection="user",
        unique_record_identifier=test_user1.id,
        record_details=data_cache
        )

    assert cache_result is None

    cache_user = await repository.get_cached_user(test_user1.id)
    assert cache_user is not None
    assert_user_matches(
        cache_user,
        user_id=data_cache['user_id'],
        email=data_cache['email'],
        unique_username=data_cache['unique_username'],
        nickname=data_cache['nickname'],
        subscriptions=data_cache['subscriptions']
        )


@pytest.mark.asyncio
async def test_get_cached_user_return_complete_user_entity(db_redis: Redis, test_user1: User):
    repository = CachedRepository(db_redis)
    cache_user = await repository.get_cached_user(test_user1.id)

    assert cache_user is None


@pytest.mark.asyncio
async def test_create_cash_article_return_complete_none(db_redis: Redis, db_session: AsyncSession, test_article: Article, test_user1: User):
    repository = CachedRepository(db_redis)
    article = await ArticleRepository(db_session).get_by_id(test_article.id)
    data_cache = {
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
    cache_result = await repository.set_cache(
        record_selection="article",
        unique_record_identifier=test_article.id,
        record_details=data_cache
        )

    assert cache_result is None

    cache_article = await repository.get_cached_article(test_article.id)
    assert cache_article is not None
    assert_article_matches(
        cache_article,
        article_id=test_article.id,
        author=test_user1,
        title=test_article.title,
        content=test_article.content,
        category=test_article.category
        )


@pytest.mark.asyncio
async def test_delete_user(db_redis: Redis, db_session: AsyncSession, test_user1: User):
    repository = CachedRepository(db_redis)

    user = await UserRepository(db_session).get_by_id(test_user1.id)
    assert user is not None
    data = {
            "user_id": user.user_id,
            "email": user.email,
            "unique_username": user.unique_username,
            "nickname": user.nickname,
            "subscriptions": json.dumps(list(user.subscriptions)),
        }
    await repository.set_cache(
        record_selection="user",
        unique_record_identifier=test_user1.id,
        record_details=data
        )

    cache_user_before_delete = await repository.get_cached_user(test_user1.id)
    assert cache_user_before_delete is not None
    assert cache_user_before_delete.email == test_user1.email

    await repository.delete_user(user)
    cache_user_after_delete = await repository.get_cached_user(test_user1.id)
    assert cache_user_after_delete is None
