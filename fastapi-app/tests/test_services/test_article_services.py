from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.application.dto.article_create_dto import ArticleCreateDTO
from app.application.services.article_service import ArticleService
from app.domain.entities.article import ArticleEntity


@pytest.fixture
def article() -> ArticleEntity:
    return ArticleEntity(
        article_id=7,
        title="Test article",
        content="Detailed test article content.",
        user_id=42,
        category="Research",
        unique_username="author",
        nickname="Author",
        likes=3,
        dislikes=1,
        created_at=datetime(2026, 8, 31, 12, 0),
    )


@pytest.fixture
def article_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def logic_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(
    article_repository: AsyncMock, logic_repository: AsyncMock
) -> ArticleService:
    return ArticleService(article_repository, logic_repository)


@pytest.mark.asyncio
async def test_submit_article_saves_complete_mapping_when_limit_allows(
    service: ArticleService,
    article_repository: AsyncMock,
    logic_repository: AsyncMock,
    article: ArticleEntity,
):
    dto = ArticleCreateDTO(
        title="Test article",
        content="Detailed test article content.",
        category="Research",
    )
    logic_repository.can_publish_today.return_value = True
    article_repository.save.return_value = article

    result = await service.submit_article(dto, user_id=42)

    assert result is article
    logic_repository.can_publish_today.assert_awaited_once_with(user_id=42)
    article_repository.save.assert_awaited_once_with(
        {
            "title": dto.title,
            "content": dto.content,
            "user_id": 42,
            "category": dto.category,
        },
        42,
    )


@pytest.mark.asyncio
async def test_submit_article_does_not_save_when_daily_limit_is_reached(
    service: ArticleService,
    article_repository: AsyncMock,
    logic_repository: AsyncMock,
):
    dto = ArticleCreateDTO(
        title="Test article",
        content="Detailed test article content.",
        category="Research",
    )
    logic_repository.can_publish_today.return_value = False

    result = await service.submit_article(dto, user_id=42)

    assert result is None
    logic_repository.can_publish_today.assert_awaited_once_with(user_id=42)
    article_repository.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_change_article_maps_dto_and_forwards_identity(
    service: ArticleService,
    article_repository: AsyncMock,
    article: ArticleEntity,
):
    dto = ArticleCreateDTO(
        title="Updated title",
        content="Updated article content.",
        category="Nutrition",
    )
    article_repository.change.return_value = article

    result = await service.change_article(dto, article_id=7, user_id=42)

    assert result is article
    article_repository.change.assert_awaited_once_with(
        {
            "title": dto.title,
            "content": dto.content,
            "category": dto.category,
        },
        7,
        42,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("service_method", "repository_method", "arguments", "expected"),
    [
        ("search_by_category", "search_by_category", ("Research",), ["article"]),
        ("delete_article", "delete", (7, 42), True),
        ("show_all_articles", "all", (), ["article"]),
        ("search_by_title", "search_by_title", ("evidence",), ["article"]),
        ("list_user_articles", "get_user_articles", (42,), ["article"]),
        ("get_by_id", "get_by_id", (7,), "article"),
        ("liked_articles_by_user", "liked_articles_by_user", (42,), ["article"]),
    ],
)
async def test_query_methods_delegate_without_changing_arguments(
    service: ArticleService,
    article_repository: AsyncMock,
    service_method: str,
    repository_method: str,
    arguments: tuple,
    expected,
):
    repository_call = getattr(article_repository, repository_method)
    repository_call.return_value = expected

    result = await getattr(service, service_method)(*arguments)

    assert result == expected
    repository_call.assert_awaited_once_with(*arguments)
