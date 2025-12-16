from fastapi import Form

from app.application.dto.articleAuth_dto import ArticleAuthDTO


async def parse_auth_form(
        email: str = Form(),
        password: str = Form(),
        nickname: str = Form(),
        username: str = Form()
) -> ArticleAuthDTO:

    return ArticleAuthDTO(
        email=email,
        password=password,
        username=username,
        nickname=nickname
    )
