import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions import NotFoundCommentError
from app.infrastructure.database.models.article import Article
from app.infrastructure.database.models.comment import Comment
from app.infrastructure.database.models.user import User
from app.infrastructure.database.repositories.comment_repository import (
    CommentRepository,
)


@pytest.mark.asyncio
async def test_create(
    db_session: AsyncSession, test_user1: User, test_article: Article
):
    repo = CommentRepository(db_session)

    mapping = {
        "content": "testcontent",
        "user_id": test_user1.id,
        "article_id": test_article.id,
    }
    comment = await repo.create(mapping)

    assert comment.article_id == test_article.id
    assert comment.user_id == test_user1.id
    assert comment.content == "testcontent"
    assert comment.unique_username == test_user1.unique_username
    assert comment.title_of_article == test_article.title


@pytest.mark.asyncio
async def test_list_by_article_id(
    db_session: AsyncSession, test_article: Article, test_comment: Comment
):
    repo = CommentRepository(db_session)

    comment = await repo.list_by_article_id(test_article.id)

    assert comment[0].content == test_comment.content


@pytest.mark.asyncio
async def test_show_by_author(
    db_session: AsyncSession, test_user1: User, test_comment: Comment
):
    repo = CommentRepository(db_session)

    comment = await repo.show_by_author(test_user1.id)

    assert comment[0].content == test_comment.content


@pytest.mark.asyncio
async def test_delete(
    db_session: AsyncSession, test_comment: Comment, test_article: Article
):
    repo = CommentRepository(db_session)

    comment = await repo.delete(test_comment.id, test_comment.user_id)

    assert comment == test_article.id

    comment = await repo.list_by_article_id(test_article.id)

    assert comment is None


@pytest.mark.asyncio
async def test_delete_rejects_non_owner(
    db_session: AsyncSession,
    test_comment: Comment,
    test_article: Article,
    test_user2: User,
):
    repo = CommentRepository(db_session)

    with pytest.raises(NotFoundCommentError):
        await repo.delete(test_comment.id, test_user2.id)

    comments = await repo.list_by_article_id(test_article.id)
    assert comments is not None
    assert comments[0].id == test_comment.id


@pytest.mark.asyncio
async def test_to_entity(
    db_session: AsyncSession,
    test_comment: Comment,
    test_user1: User,
    test_article: Article,
):
    repo = CommentRepository(db_session)

    comment = await repo._to_entity([test_comment])

    assert comment[0].title_of_article == test_article.title
    assert comment[0].user_id == test_comment.user_id
    assert comment[0].article_id == test_comment.article_id
    assert comment[0].content == test_comment.content
    assert comment[0].created_at == test_comment.created_at
    assert comment[0].nickname == test_user1.nickname
    assert comment[0].unique_username == test_user1.unique_username
