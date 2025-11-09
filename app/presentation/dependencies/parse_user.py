from fastapi import Form

from app.application.dto.articleAuth_dto import ArticleAuthDTO
from app.domain.logging import logger


async def parse_auth_form(
        email: str = Form(),
        password: str = Form(),
        username: str = Form()
) -> ArticleAuthDTO:
    logger.info(f'start dependencies with date of {email, password, username}')
    return ArticleAuthDTO(
        email=email,
        password=password,
        username=username
    )
