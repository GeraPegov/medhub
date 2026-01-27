import pytest

from app.infrastructure.database.repositories.article_repository import (
    ArticleRepository,
)
from app.infrastructure.database.repositories.logic_repository import LogicRepository


@pytest.mark.asyncio
async def test_check_limited(db_session, test_user1):
    repo_logic = LogicRepository(db_session)
    repo_article = ArticleRepository(db_session)

    mapping = {
        'title': 'testtitle',
        'content': 'testcontent',
        'user_id': test_user1.id,
        'category': 'testcategory'
    }

    for _ in range(2):
        await repo_article.save(mapping, test_user1.id)

    result = await repo_logic.check_limited(test_user1.id)
    assert result is True

    await repo_article.save(mapping, test_user1.id)
    result = await repo_logic.check_limited(test_user1.id)
    assert result is False

