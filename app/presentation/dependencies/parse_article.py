
from fastapi import Form

from app.application.dto.articleCreate_dto import ArticleCreateDTO


async def parse_article_form(
        title: str = Form(),
        content: str = Form(),
        category:str = Form()
    ) -> ArticleCreateDTO:

    return ArticleCreateDTO(
        title=title,
        content=content,
        category=category
    )

