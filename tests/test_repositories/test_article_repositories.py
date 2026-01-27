import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.article import Article
from app.infrastructure.database.models.user import User
from app.infrastructure.database.repositories.article_repository import (
    ArticleRepository,
)


@pytest.mark.asyncio
async def test_save(db_session: AsyncSession, test_user1: User):
    repo = ArticleRepository(db_session)
    mapping = {
        'title': 'testtitle',
        'content': 'testcontent',
        'user_id': test_user1.id,
        'category': 'testcategory'
    }

    article = await repo.save(
        mapping=mapping,
        user_id=test_user1.id
    )

    assert article.title == 'testtitle'
    assert article.content == 'testcontent'
    assert article.user_id == test_user1.id
    assert article.category == 'testcategory'

@pytest.mark.asyncio
async def test_get_by_id(db_session: AsyncSession, test_article: Article):
    repo = ArticleRepository(db_session)
    article = await repo.get_by_id(test_article.id)

    assert article.article_id == test_article.id


@pytest.mark.asyncio
async def test_get_by_all(db_session: AsyncSession, test_article: Article):
    repo = ArticleRepository(db_session)
    article = await repo.all()

    assert type(article) is list
    assert len(article) == 1
    assert article[0].article_id == test_article.id


@pytest.mark.asyncio
async def test_delete(db_session: AsyncSession, test_article: Article):
    repo = ArticleRepository(db_session)

    article = await repo.delete(test_article.id)

    assert await repo.get_by_id(test_article.id) is None
    assert article is True


@pytest.mark.asyncio
async def test_search_by_title(db_session: AsyncSession, test_article: Article):
    repo = ArticleRepository(db_session)

    article1 = await repo.search_by_title(test_article.title)
    article2 = await repo.search_by_title(test_article.title[:5])

    assert article1[0].title == test_article.title
    assert article2[0].title == test_article.title


@pytest.mark.asyncio
async def test_get_user_articles(db_session: AsyncSession, test_user1: User):
    repo = ArticleRepository(db_session)
    mapping = {
        'title': 'testtitle',
        'content': 'testcontent',
        'user_id': test_user1.id,
        'category': 'testcategory'
    }
    await repo.save(
        mapping=mapping,
        user_id=test_user1.id
    )

    articles = await repo.get_user_articles(test_user1.id)

    assert articles[0].title == 'testtitle'
    assert articles[0].unique_username == test_user1.unique_username


@pytest.mark.asyncio
async def test_search_by_category(db_session: AsyncSession, test_article: Article):
    repo = ArticleRepository(db_session)

    articles = await repo.search_by_category(test_article.category)

    assert articles[0].category == test_article.category


@pytest.mark.asyncio
async def test_change(db_session: AsyncSession, test_article: Article):
    repo = ArticleRepository(db_session)

    old_article = await repo.get_by_id(test_article.id)

    assert old_article.article_id == test_article.id
    assert old_article.title == 'testtitle for you'
    assert old_article.content == 'testcontent'
    assert old_article.category == 'testcategory'

    mapping = {
        'title': 'testchangetitle',
        'content': 'testchangecontent',
        'category': 'testchangecategory'
    }
    new_article = await repo.change(
        article_id=test_article.id,
        mapping=mapping
    )

    assert new_article.article_id == test_article.id
    assert new_article.title == 'testchangetitle'
    assert new_article.content == 'testchangecontent'
    assert new_article.category == 'testchangecategory'

@pytest.mark.asyncio
async def test_to_entity(
    db_session: AsyncSession,
    test_article: Article,
    test_user1: User
    ):
    repo = ArticleRepository(db_session)

    article = await repo._to_entity([test_article])

    assert article[0].article_id == test_article.id
    assert article[0].title == test_article.title
    assert article[0].content == test_article.content
    assert article[0].unique_username == test_user1.unique_username
    assert article[0].nickname == test_user1.nickname
    assert article[0].created_at == test_article.created_at
    assert article[0].user_id == test_article.user_id
    assert article[0].category == test_article.category
