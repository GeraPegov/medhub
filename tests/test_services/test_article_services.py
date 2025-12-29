from datetime import datetime
from unittest.mock import Mock
import pytest

from app.application.dto.articleCreate_dto import ArticleCreateDTO
from app.application.services.article_service import ArticleService
from app.domain.entities.article import ArticleEntity


@pytest.mark.asyncio
async def test_mock_service_article_true(mock_logic_db_repository, mock_article_db_repository):
    base_service = ArticleService(
        base_repository=mock_article_db_repository,
        logic_repository=mock_logic_db_repository
    )

    mock_logic_db_repository.check_limited.return_value = True
    mock_article_db_repository.save.return_value = ArticleEntity(
        article_id=1,
        title='Test',
        content='Contentcontent',
        author_id=123,
        category='Tech',
        unique_username='testuser',
        nickname='Test User',
        created_at=datetime.now())

    dto = ArticleCreateDTO(
        title='title',
        category='category',
        content='contentcontent'
    )
    result = await base_service.submit_article(dto, 123)
    assert result.author_id == 123
    assert result.title == 'Test'


@pytest.mark.asyncio()
async def test_mock_service_article_false(mock_logic_db_repository, mock_article_db_repository):
    base_service = ArticleService(
        base_repository=mock_article_db_repository,
        logic_repository=mock_logic_db_repository
    )

    mock_logic_db_repository.check_limited.return_value = False
    dto = ArticleCreateDTO(
        title='title',
        category='category',
        content='contentcontent'
    )
    result = await base_service.submit_article(dto, 123)

    assert result is None

