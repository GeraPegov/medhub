import secrets

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import SQLAlchemyError

from app.application.dto.article_auth_dto import UserDTO
from app.application.services.register_user import UserRegistrationService
from app.application.services.security.login_user import UserAuthenticationService
from app.domain.exceptions import (
    NotFoundUserError,
    NotValidCsrfTokenError,
    NotValidPasswordError,
    UserAlreadyExistsError,
    UsernameAlreadyExistsError,
)
from app.presentation.dependencies.auth import (
    get_auth_login,
    get_auth_registration,
)
from app.presentation.dependencies.parse_user import parse_auth_form

router = APIRouter()
templates = Jinja2Templates("app/presentation/api/endpoints/templates/html")


async def check_csrf_token(request: Request, csrf_token):
    expected = request.session.get("csrf_token")
    if not expected or not secrets.compare_digest(expected, csrf_token):
        raise NotValidCsrfTokenError
    return


@router.get("/auth")
def page_of_login(request: Request):
    if "csrf_token" not in request.session:
        request.session["csrf_token"] = secrets.token_urlsafe(32)
    return templates.TemplateResponse(request=request, name="login.html")


@router.post("/auth/login")
async def login(
    request: Request,
    response: Response,
    csrf_token: str = Form(...),
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: UserAuthenticationService = Depends(get_auth_login),
):
    try:
        await check_csrf_token(request, csrf_token)
        token = await auth_service.execute(
            email=form_data.username, password=form_data.password
        )

        response = RedirectResponse(url="/", status_code=303)

        response.set_cookie(
            key="access_token", value=token, httponly=True, samesite="lax"
        )

        return response
    except (NotValidPasswordError, NotFoundUserError):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Неправильный логин или пароль"},
            status_code=401,
        )
    except NotValidCsrfTokenError:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Неверный токен"},
            status_code=403,
        )


@router.get("/register")
async def page_of_register(request: Request):
    if "csrf_token" not in request.session:
        request.session["csrf_token"] = secrets.token_urlsafe(32)
    return templates.TemplateResponse(request=request, name="register.html")


@router.post("/auth/register")
async def register(
    request: Request,
    csrf_token: str = Form(...),
    user_data: UserDTO = Depends(parse_auth_form),
    registration_service: UserRegistrationService = Depends(get_auth_registration),
):
    try:
        await check_csrf_token(request, csrf_token)
        await registration_service.execute(user_data)
        return RedirectResponse(url="/auth", status_code=303)
    except NotValidCsrfTokenError:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": "Неправильный токен"},
            status_code=403,
        )
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
