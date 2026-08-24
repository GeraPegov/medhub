from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import SQLAlchemyError

from app.application.dto.article_auth_dto import UserDTO
from app.application.services.register_user import UserRegistrationService
from app.domain.exceptions import UserAlreadyExistsError, UsernameAlreadyExistsError
from app.presentation.dependencies.auth import get_auth_registration
from app.presentation.dependencies.parse_user import parse_auth_form

router = APIRouter()

templates = Jinja2Templates("app/presentation/api/endpoints/templates/html")


@router.get("/register")
async def page_of_register(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")


@router.post("/auth/register")
async def register(
    request: Request,
    user_data: UserDTO = Depends(parse_auth_form),
    registration_service: UserRegistrationService = Depends(get_auth_registration),
):
    try:
        await registration_service.execute(user_data)
        return RedirectResponse(url="/auth", status_code=303)
    except UserAlreadyExistsError:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": "Пользователь с таким email уже существует."},
            status_code=409,
        )
    except UsernameAlreadyExistsError:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": "Пользователь с таким username уже существует."},
            status_code=409,
        )
    except SQLAlchemyError:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": "Не удалось завершить регистрацию. Попробуйте позже."},
            status_code=500,
        )
