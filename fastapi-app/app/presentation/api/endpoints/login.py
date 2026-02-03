from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from app.application.services.security.login_user import UserAuthenticationService
from app.presentation.dependencies.auth import (
    get_auth_login,
)

router = APIRouter()
templates = Jinja2Templates('app/presentation/api/endpoints/templates/html')


@router.get('/auth')
def page_of_login(request: Request):
    return templates.TemplateResponse(
        'login.html',
        {'request': request}
    )

@router.post('/auth/login')
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: UserAuthenticationService = Depends(get_auth_login),
):
    token = await auth_service.execute(
        email=form_data.username,
        password=form_data.password
    )
    if not token:
        return templates.TemplateResponse(
        'login.html',
        {
        'request': request,
        'error': 'Неправильный логин или пароль'
        }
    )

    response = RedirectResponse(
        url='/',
        status_code=303
    )

    response.set_cookie(
        key='access_token',
        value=token,
        httponly=True,
        samesite='lax'
    )

    return response
