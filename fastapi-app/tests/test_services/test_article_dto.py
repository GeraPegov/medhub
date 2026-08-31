import pytest
from pydantic import ValidationError

from app.application.dto.article_create_dto import ArticleCreateDTO


def test_article_create_dto_accepts_boundary_lengths():
    dto = ArticleCreateDTO(
        title="abc",
        content="x" * 10,
        category="Research",
    )

    assert dto.title == "abc"
    assert dto.content == "x" * 10
    assert dto.category == "Research"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", "ab"),
        ("title", "x" * 201),
        ("content", "x" * 9),
        ("content", "x" * 10_001),
    ],
)
def test_article_create_dto_rejects_out_of_range_text(field: str, value: str):
    data = {
        "title": "Valid title",
        "content": "Valid article content.",
        "category": "Research",
    }
    data[field] = value

    with pytest.raises(ValidationError) as error:
        ArticleCreateDTO(**data)

    assert error.value.errors()[0]["loc"] == (field,)
