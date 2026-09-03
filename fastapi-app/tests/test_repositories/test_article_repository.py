import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.article import ArticleEntity
from app.domain.exceptions import NotFoundArticleError, ReactionAlreadyExistsError
from app.infrastructure.database.models.article import Article
from app.infrastructure.database.models.user import User
from app.infrastructure.database.repositories.article_repository import (
    ArticleRepository,
)


def article_data(user_id: int, **overrides) -> dict:
    data = {
        "title": "Evidence based medicine",
        "content": "A sufficiently detailed article body",
        "user_id": user_id,
        "category": "Research",
    }
    data.update(overrides)
    return data


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

# def assert_article_matches_model(article: ArticleEntity, data: dict, author: User):
#     return assert_article_matches(
#         article,
#         article_id=
#         )


@pytest.mark.asyncio
async def test_save_returns_complete_article_entity(
    db_session: AsyncSession, test_user1: User
):
    repository = ArticleRepository(db_session)
    data = article_data(test_user1.id)

    article = await repository.save(data, test_user1.id)

    assert_article_matches(
        article,
        article_id=article.article_id,
        author=test_user1,
        title=data["title"],
        content=data["content"],
        category=data["category"],
    )


@pytest.mark.asyncio
async def test_get_by_id_returns_complete_entity(
    db_session: AsyncSession, test_article: Article, test_user1: User
):
    repository = ArticleRepository(db_session)

    article = await repository.get_by_id(test_article.id)

    assert_article_matches(
        article,
        article_id=test_article.id,
        author=test_user1,
        title=test_article.title,
        content=test_article.content,
        category=test_article.category,
    )


@pytest.mark.asyncio
async def test_get_by_id_raises_for_missing_article(db_session: AsyncSession):
    repository = ArticleRepository(db_session)

    with pytest.raises(NotFoundArticleError):
        await repository.get_by_id(999_999)


@pytest.mark.asyncio
async def test_all_returns_none_when_there_are_no_articles(db_session: AsyncSession):
    repository = ArticleRepository(db_session)

    assert await repository.all() is None


@pytest.mark.asyncio
async def test_all_returns_every_article(db_session: AsyncSession, test_user1: User):
    repository = ArticleRepository(db_session)
    first = await repository.save(
        article_data(test_user1.id, title="First article"), test_user1.id
    )
    second = await repository.save(
        article_data(test_user1.id, title="Second article"), test_user1.id
    )

    articles = await repository.all()

    assert articles is not None
    assert {article.article_id for article in articles} == {
        first.article_id,
        second.article_id,
    }
    assert {article.title for article in articles} == {
        "First article",
        "Second article",
    }


@pytest.mark.asyncio
async def test_search_by_title_is_partial_and_case_insensitive(
    db_session: AsyncSession, test_user1: User
):
    repository = ArticleRepository(db_session)
    expected = await repository.save(
        article_data(test_user1.id, title="Evidence Based Medicine"), test_user1.id
    )
    await repository.save(
        article_data(test_user1.id, title="Nutrition basics"), test_user1.id
    )

    articles = await repository.search_by_title("bAsEd")

    assert articles is not None
    assert [article.article_id for article in articles] == [expected.article_id]


@pytest.mark.asyncio
async def test_search_by_title_returns_none_without_matches(
    db_session: AsyncSession, test_article: Article
):
    repository = ArticleRepository(db_session)

    assert await repository.search_by_title("no such title") is None


@pytest.mark.asyncio
async def test_search_by_category_returns_exact_matches_only(
    db_session: AsyncSession, test_user1: User
):
    repository = ArticleRepository(db_session)
    expected = await repository.save(
        article_data(test_user1.id, title="Research article", category="Research"),
        test_user1.id,
    )
    await repository.save(
        article_data(test_user1.id, title="Nutrition article", category="Nutrition"),
        test_user1.id,
    )

    articles = await repository.search_by_category("Research")

    assert articles is not None
    assert [article.article_id for article in articles] == [expected.article_id]


@pytest.mark.asyncio
async def test_search_by_category_returns_none_without_matches(
    db_session: AsyncSession, test_article: Article
):
    repository = ArticleRepository(db_session)

    assert await repository.search_by_category("Unknown") is None


@pytest.mark.asyncio
async def test_get_user_articles_does_not_return_another_authors_articles(
    db_session: AsyncSession, test_user1: User, test_user2: User
):
    repository = ArticleRepository(db_session)
    expected = await repository.save(
        article_data(test_user1.id, title="First author's article"), test_user1.id
    )
    await repository.save(
        article_data(test_user2.id, title="Second author's article"), test_user2.id
    )

    articles = await repository.get_user_articles(test_user1.id)

    assert articles is not None
    assert [article.article_id for article in articles] == [expected.article_id]


@pytest.mark.asyncio
async def test_get_user_articles_returns_none_without_matches(
    db_session: AsyncSession, test_user1: User
):
    repository = ArticleRepository(db_session)

    assert await repository.get_user_articles(test_user1.id) is None


@pytest.mark.asyncio
async def test_change_updates_all_editable_fields_for_owner(
    db_session: AsyncSession, test_article: Article, test_user1: User
):
    repository = ArticleRepository(db_session)
    changes = {
        "title": "Updated title",
        "content": "Updated article content.",
        "category": "Updated category",
    }

    article = await repository.change(
        changes, article_id=test_article.id, user_id=test_article.user_id
    )
    assert_article_matches(
        article,
        article_id=test_article.id,
        author=test_user1,
        title=changes["title"],
        content=changes["content"],
        category=changes["category"]
    )


@pytest.mark.asyncio
async def test_change_rejects_non_owner_and_preserves_article(
    db_session: AsyncSession, test_article: Article, test_user2: User
):
    repository = ArticleRepository(db_session)
    article_id = test_article.id
    original = await repository.get_by_id(article_id)
    changes = {
        "title": "Hacked title",
        "content": "Hacked article content.",
        "category": "Hacked category",
    }

    with pytest.raises(NotFoundArticleError):
        await repository.change(changes, article_id, test_user2.id)

    unchanged = await repository.get_by_id(article_id)
    assert unchanged.title == original.title
    assert unchanged.content == original.content
    assert unchanged.category == original.category


@pytest.mark.asyncio
async def test_delete_removes_owners_article(
    db_session: AsyncSession, test_article: Article
):
    repository = ArticleRepository(db_session)

    assert await repository.delete(test_article.id, test_article.user_id) is True
    with pytest.raises(NotFoundArticleError):
        await repository.get_by_id(test_article.id)


@pytest.mark.asyncio
async def test_delete_rejects_non_owner_and_preserves_article(
    db_session: AsyncSession, test_article: Article, test_user2: User
):
    repository = ArticleRepository(db_session)
    article_id = test_article.id

    with pytest.raises(NotFoundArticleError):
        await repository.delete(article_id, test_user2.id)

    assert (await repository.get_by_id(article_id)).article_id == article_id


@pytest.mark.asyncio
async def test_delete_raises_for_missing_article(db_session: AsyncSession):
    repository = ArticleRepository(db_session)

    with pytest.raises(NotFoundArticleError):
        await repository.delete(999_999, 999_999)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("reaction", "expected_likes", "expected_dislikes"),
    [("like", 1, 0), ("dislike", 0, 1)],
)
async def test_set_reaction_increments_requested_counter(
    db_session: AsyncSession,
    test_article: Article,
    test_user1: User,
    reaction: str,
    expected_likes: int,
    expected_dislikes: int,
):
    repository = ArticleRepository(db_session)

    article = await repository.set_reaction(
        article_id=test_article.id,
        user_id=test_user1.id,
        reaction=reaction,
    )

    assert article.likes == expected_likes
    assert article.dislikes == expected_dislikes


@pytest.mark.asyncio
async def test_second_reaction_is_rejected_without_changing_counters(
    db_session: AsyncSession, test_article: Article, test_user1: User
):
    repository = ArticleRepository(db_session)
    article_id = test_article.id
    await repository.set_reaction(article_id, test_user1.id, "like")

    with pytest.raises(ReactionAlreadyExistsError):
        await repository.set_reaction(article_id, test_user1.id, "dislike")

    article = await repository.get_by_id(article_id)
    assert article.likes == 1
    assert article.dislikes == 0


@pytest.mark.asyncio
async def test_set_reaction_raises_for_missing_article(
    db_session: AsyncSession, test_user1: User
):
    repository = ArticleRepository(db_session)

    with pytest.raises(NotFoundArticleError):
        await repository.set_reaction(999_999, test_user1.id, "like")


@pytest.mark.asyncio
async def test_liked_articles_returns_only_articles_liked_by_user(
    db_session: AsyncSession, test_user1: User
):
    repository = ArticleRepository(db_session)
    liked = await repository.save(
        article_data(test_user1.id, title="Liked article"), test_user1.id
    )
    disliked = await repository.save(
        article_data(test_user1.id, title="Disliked article"), test_user1.id
    )
    await repository.set_reaction(liked.article_id, test_user1.id, "like")
    await repository.set_reaction(disliked.article_id, test_user1.id, "dislike")

    articles = await repository.liked_articles_by_user(test_user1.id)

    assert articles is not None
    assert [article.article_id for article in articles] == [liked.article_id]


@pytest.mark.asyncio
async def test_liked_articles_returns_none_when_user_has_no_likes(
    db_session: AsyncSession, test_user1: User
):
    repository = ArticleRepository(db_session)

    assert await repository.liked_articles_by_user(test_user1.id) is None
