from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse

from app.application.services.comment_service import CommentService
from app.domain.entities.user import UserEntity
from app.domain.exceptions import (
    NotFoundCommentError,
    NotFoundUserError,
    NotValidCredentialsError,
    NotValidCsrfTokenError,
)
from app.presentation.api.endpoints.auth import check_csrf_token
from app.presentation.dependencies.comments import get_comment_service
from app.presentation.dependencies.current_user import get_current_user

router = APIRouter()


@router.post("/comments/{article_id}/create")
async def create(
    request: Request,
    article_id: int,
    content: str = Form(...),
    csrf_token: str = Form(...),
    comment_service: CommentService = Depends(get_comment_service),
    current_user: UserEntity | None = Depends(get_current_user),
):
    try:
        if not current_user:
            return RedirectResponse("/auth", status_code=303)
        await check_csrf_token(request, csrf_token)
        await comment_service.create(
            article_id=article_id,
            content=content,
            user_id=current_user.user_id,
        )

        response = RedirectResponse(url=f"/article/{article_id}", status_code=303)

        return response
    except NotValidCredentialsError:
        return JSONResponse(
            {"error": "Не существует пользователя или статьи"},
            status_code=404,
        )
    except NotValidCsrfTokenError:
        return JSONResponse(
            {"error": "Неверный токен"},
            status_code=403,
        )


@router.post("/comments/{comment_id}/delete")
async def delete(
    request: Request,
    comment_id: int,
    csrf_token: str = Form(...),
    comment_service: CommentService = Depends(get_comment_service),
    current_user: UserEntity | None = Depends(get_current_user),
):
    try:
        if not current_user:
            return RedirectResponse("/auth", status_code=303)
        await check_csrf_token(request, csrf_token)
        article_id = await comment_service.delete(
            comment_id=comment_id,
            user_id=current_user.user_id,
        )

        response = RedirectResponse(url=f"/article/{article_id}", status_code=303)
        return response
    except NotValidCsrfTokenError:
        return JSONResponse(
            {"error": "Неверный токен"},
            status_code=403,
        )
    except NotFoundCommentError:
        return JSONResponse(
            {"error": "Комментарий не найден"},
            status_code=404,
        )
    except NotFoundUserError:
        return JSONResponse(
            {"error": "Нет доступа у пользователя"},
            status_code=401,
        )
