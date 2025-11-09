from fastapi import Form

from app.application.dto.articleCreate_dto import ArticleCreateDTO


async def parse_article_form(
        author: str = Form(),
        title: str = Form(),
        content: str = Form()
    ) -> ArticleCreateDTO:
    return ArticleCreateDTO(
        author=author,
        title=title,
        content=content
    )

