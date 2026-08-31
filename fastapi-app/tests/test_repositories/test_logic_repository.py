from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.article import Article
from app.infrastructure.database.models.user import User
from app.infrastructure.database.repositories.article_repository import (
    ArticleRepository,
)
from app.infrastructure.database.repositories.logic_repository import LogicRepository


def article_data(user_id: int, title: str) -> dict:
    return {
        "title": title,
        "content": "A sufficiently detailed article body.",
        "user_id": user_id,
        "category": "Research",
    }


@pytest.mark.asyncio
async def test_publication_limit_counts_only_articles_created_today(
    db_session: AsyncSession, test_user1: User
):
    logic_repository = LogicRepository(db_session)
    article_repository = ArticleRepository(db_session)
    old_article = Article(
        **article_data(test_user1.id, "Yesterday's article"),
        users=test_user1,
        created_at=datetime.now() - timedelta(days=1),
    )
    db_session.add(old_article)
    await db_session.commit()

    for index in range(2):
        await article_repository.save(
            article_data(test_user1.id, f"Today's article {index}"),
            test_user1.id,
        )

    assert await logic_repository.can_publish_today(test_user1.id) is True

    await article_repository.save(
        article_data(test_user1.id, "Today's third article"),
        test_user1.id,
    )

    assert await logic_repository.can_publish_today(test_user1.id) is False


@pytest.mark.asyncio
async def test_publication_limit_is_scoped_to_author(
    db_session: AsyncSession, test_user1: User, test_user2: User
):
    logic_repository = LogicRepository(db_session)
    article_repository = ArticleRepository(db_session)
    for index in range(3):
        await article_repository.save(
            article_data(test_user1.id, f"First author article {index}"),
            test_user1.id,
        )

    assert await logic_repository.can_publish_today(test_user1.id) is False
    assert await logic_repository.can_publish_today(test_user2.id) is True
