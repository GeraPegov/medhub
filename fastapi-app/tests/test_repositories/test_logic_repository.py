import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.user import User
from app.infrastructure.database.repositories.article_repository import (
    ArticleRepository,
)
from app.infrastructure.database.repositories.logic_repository import LogicRepository


@pytest.mark.asyncio
async def test_check_limited(db_session: AsyncSession, test_user1: User):
    logic_repository = LogicRepository(db_session)
    article_repository = ArticleRepository(db_session)

    mapping = {
        "title": "testtitle",
        "content": "testcontent",
        "user_id": test_user1.id,
        "category": "testcategory",
    }

    for _ in range(2):
        await article_repository.save(mapping, test_user1.id)

    result = await logic_repository.can_publish_today(test_user1.id)
    assert result is True

    await article_repository.save(mapping, test_user1.id)
    result = await logic_repository.can_publish_today(test_user1.id)
    assert result is False
