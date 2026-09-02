from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.comment import CommentEntity
from app.domain.exceptions import (
    NotFoundArticleError,
    NotFoundCommentError,
    NotFoundUserError,
)
from app.infrastructure.database.models.article import Article
from app.infrastructure.database.models.comment import Comment
from app.infrastructure.database.models.user import User
from app.infrastructure.database.repositories.comment_repository import (
    CommentRepository,
)


def data_comment(user_id: int, article_id: int, **overrides):
    data = {
        "content": "testcontent",
        "user_id": user_id,
        "article_id": article_id,
    }
    data.update(overrides)
    return data


def assert_comment_matches(
    comment: CommentEntity,
    *,
    comment_id: int,
    article_id: int,
    user_id: int,
    content: str,
    nickname: str,
    unique_username: str,
    title_of_article: str,
    created_at: datetime,
):
    assert comment.id == comment_id
    assert comment.article_id == article_id
    assert comment.user_id == user_id
    assert comment.content == content
    assert comment.nickname == nickname
    assert comment.unique_username == unique_username
    assert comment.title_of_article == title_of_article
    assert comment.created_at == created_at


def assert_comment_matches_model(
    comment: CommentEntity, user: User, article: Article, model: Comment
):
    assert_comment_matches(
        comment,
        comment_id=model.id,
        article_id=article.id,
        user_id=user.id,
        content=model.content,
        nickname=user.nickname,
        unique_username=user.unique_username,
        title_of_article=article.title,
        created_at=model.created_at,
    )


@pytest.mark.asyncio
async def test_create_returns_complete_comment_entity(
    db_session: AsyncSession, test_user1: User, test_article: Article
):
    repository = CommentRepository(db_session)
    data = data_comment(test_user1.id, test_article.id)
    comment = await repository.create(data)
    stored_comment = (
        await db_session.execute(select(Comment).where(Comment.id == comment.id))
    ).scalar_one_or_none()
    assert stored_comment is not None
    assert stored_comment.content == data["content"]
    assert isinstance(comment.created_at, datetime)
    assert_comment_matches_model(
        comment,
        test_user1,
        test_article,
        stored_comment,
    )


@pytest.mark.asyncio
async def test_create_raises_user_not_found_error(
    db_session: AsyncSession, test_article: Article
):
    repository = CommentRepository(db_session)
    data = data_comment(999, test_article.id)
    with pytest.raises(NotFoundUserError):
        await repository.create(data)


@pytest.mark.asyncio
async def test_create_raises_article_not_found_error(
    db_session: AsyncSession, test_user1: User
):
    repository = CommentRepository(db_session)
    data = data_comment(test_user1.id, 999)
    with pytest.raises(NotFoundArticleError):
        await repository.create(data)


@pytest.mark.asyncio
async def test_list_by_article_id_returns_comments_list(
    db_session: AsyncSession,
    test_article: Article,
    test_comment: Comment,
    test_user1: User,
):
    repository = CommentRepository(db_session)
    comment = await repository.list_by_article_id(test_article.id)
    assert comment is not None
    assert len(comment) == 1
    assert_comment_matches(
        comment[0],
        comment_id=test_comment.id,
        article_id=test_article.id,
        user_id=test_user1.id,
        content=test_comment.content,
        nickname=test_user1.nickname,
        unique_username=test_user1.unique_username,
        title_of_article=test_article.title,
        created_at=test_comment.created_at,
    )


@pytest.mark.asyncio
async def test_list_by_article_id_returns_none_when_article_has_no_comments(
    db_session: AsyncSession, test_article: Article
):
    repository = CommentRepository(db_session)
    comment = await repository.list_by_article_id(test_article.id)
    assert comment is None


@pytest.mark.asyncio
async def test_list_by_author_returns_comments_list(
    db_session: AsyncSession,
    test_user1: User,
    test_comment: Comment,
    test_article: Article,
):
    repository = CommentRepository(db_session)
    comment = await repository.list_by_author(test_user1.id)
    assert comment is not None
    assert len(comment) == 1
    assert_comment_matches(
        comment[0],
        comment_id=test_comment.id,
        article_id=test_article.id,
        user_id=test_user1.id,
        content=test_comment.content,
        nickname=test_user1.nickname,
        unique_username=test_user1.unique_username,
        title_of_article=test_article.title,
        created_at=test_comment.created_at,
    )


@pytest.mark.asyncio
async def test_list_by_author_returns_none_when_author_has_no_comments(
    db_session: AsyncSession, test_user1: User
):
    repository = CommentRepository(db_session)
    comment = await repository.list_by_author(test_user1.id)
    assert comment is None


@pytest.mark.asyncio
async def test_delete_returns_article_id_and_removes_only_requested_comment(
    db_session: AsyncSession, test_comment: Comment, test_article: Article
):
    repository = CommentRepository(db_session)
    sibling = await repository.create(
        data_comment(test_comment.user_id, test_article.id, content="Keep this comment")
    )

    article_id = await repository.delete(test_comment.id, test_comment.user_id)
    assert type(article_id) is int
    assert article_id == test_article.id

    check_comment_after_delete = (
        await db_session.execute(select(Comment).where(Comment.id == test_comment.id))
    ).scalar_one_or_none()
    assert check_comment_after_delete is None
    remaining_ids = (await db_session.execute(select(Comment.id))).scalars().all()
    assert remaining_ids == [sibling.id]


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
    assert len(comments) == 1
    assert comments[0].id == test_comment.id


@pytest.mark.asyncio
async def test_to_entity(
    db_session: AsyncSession,
    test_comment: Comment,
    test_user1: User,
    test_article: Article,
):
    repository = CommentRepository(db_session)
    comment = await repository._to_entity([test_comment])

    assert len(comment) == 1
    assert_comment_matches(
        comment[0],
        comment_id=test_comment.id,
        article_id=test_article.id,
        user_id=test_user1.id,
        content=test_comment.content,
        nickname=test_user1.nickname,
        unique_username=test_user1.unique_username,
        title_of_article=test_article.title,
        created_at=test_comment.created_at,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["list_by_article_id", "list_by_author"])
async def test_list_filters_comments_by_requested_id(
    db_session: AsyncSession,
    test_comment: Comment,
    test_article: Article,
    test_user1: User,
    test_user2: User,
    method: str,
):
    repository = CommentRepository(db_session)
    other_article = Article(
        title="Other article",
        content="Other article content",
        category="Research",
        user_id=test_user2.id,
        users=test_user2,
    )
    db_session.add(other_article)
    await db_session.commit()

    other_author_comment = await repository.create(
        data_comment(test_user2.id, test_article.id)
    )
    other_article_comment = await repository.create(
        data_comment(test_user1.id, other_article.id)
    )

    if method == "list_by_article_id":
        comments = await repository.list_by_article_id(test_article.id)
        expected_ids = {test_comment.id, other_author_comment.id}
    else:
        comments = await repository.list_by_author(test_user1.id)
        expected_ids = {test_comment.id, other_article_comment.id}

    assert comments is not None
    assert len(comments) == len(expected_ids)
    assert {comment.id for comment in comments} == expected_ids


@pytest.mark.asyncio
async def test_delete_raises_when_comment_does_not_exist(
    db_session: AsyncSession, test_user1: User
):
    repository = CommentRepository(db_session)

    with pytest.raises(NotFoundCommentError):
        await repository.delete(999, test_user1.id)
