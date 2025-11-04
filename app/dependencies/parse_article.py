from fastapi import Form

from app.models.dto import ArticleCreateDTO, ArticleRegisterDTO


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


async def parse_register_form(
        email: str = Form(),
        password: str = Form(),
        password_confirm: str = Form()
) -> ArticleRegisterDTO:
    return ArticleRegisterDTO(
        email=email,
        password=password,
        password_confirm=password_confirm
    )
