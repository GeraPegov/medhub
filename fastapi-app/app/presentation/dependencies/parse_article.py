from fastapi import Form
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.application.dto.article_create_dto import ArticleCreateDTO


async def parse_article_form(
    title: str = Form(), content: str = Form(), category: str = Form()
) -> ArticleCreateDTO:
    try:
        return ArticleCreateDTO(title=title, content=content, category=category)
    except ValidationError as error:
        raise RequestValidationError(error.errors()) from error
