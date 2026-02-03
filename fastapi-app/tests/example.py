import json

import pytest

from app.infrastructure.database.models.article import Article
from app.infrastructure.database.models.comment import Comments
from app.infrastructure.database.models.user import User


@pytest.fixture
async def test_user1(db_session):
    user = User(
        email='test1@example.com',
        password_hash='testpassword1',
        unique_username='testusername1',
        nickname='testnickname1',
        subscriptions=['Ivan']
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def test_user2(db_session):
    user = User(
        email='test2@example.com',
        password_hash='testpassword2',
        unique_username='testusername2',
        nickname='testnickname2',
        subscriptions=['Anton']
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def test_article(db_session, test_user1):
    article = Article(
        title='testtitle for you',
        content='testcontent',
        author_id='testauthor_id',
        author=test_user1,
        category='testcategory'
    )

    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)

    return article


@pytest.fixture
async def test_comment(db_session, test_user1, test_article):
    comment = Comments(
        content='test_content',
        author_id=test_user1.id,
        article_id=test_article.id,
        article=test_article,
        author=test_user1
    )

    db_session.add(comment)
    await db_session.commit()
    await db_session.refresh(comment)

    return comment


@pytest.fixture
async def test_cache_user_example(db_redis, test_user1):
    mapping = {
        'user_id': str(test_user1.id),
        'email': test_user1.email,
        'unique_username': test_user1.unique_username,
        'nickname': test_user1.nickname,
        'subscriptions': json.dumps(list(test_user1.subscriptions))
    }

    await db_redis.hset(f'user:{test_user1.id}', mapping=mapping)
    await db_redis.hset(f'user:{test_user1.unique_username}', mapping=mapping)
    await db_redis.expire(f'user:{1}', 3600)
    cache = await db_redis.hgetall(f'user:{1}')

    return cache

@pytest.fixture
async def test_cache_article_example(db_redis, test_article, test_user1):
    mapping = {
        'unique_username': test_user1.unique_username,
        'title': test_article.title,
        'content': test_article.content,
        'author_id': test_article.author_id,
        'nickname': test_user1.nickname,
        'created_at': test_article.created_at.timestamp(),
        'category': test_article.category,
        'article_id': test_article.id
    }

    await db_redis.hset(f'article:{test_article.id}', mapping=mapping)
    await db_redis.expire(f'article:{1}', 3600)
    cache = await db_redis.hgetall(f'article:{1}')

    return cache

