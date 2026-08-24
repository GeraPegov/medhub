from fastapi import Form

from app.application.dto.article_auth_dto import UserDTO


async def parse_auth_form(
    email: str = Form(...),
    password: str = Form(...),
    nickname: str = Form(...),
    username: str = Form(...),
) -> UserDTO:

    return UserDTO(email=email, password=password, username=username, nickname=nickname)
