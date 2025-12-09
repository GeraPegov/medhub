from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from app.application.services.login_user import UserAuthenticationService
from app.domain.logging import logger
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.security.auth_service import AuthService
from app.presentation.dependencies.auth import get_auth_service, get_user_repository

router = APIRouter()
templates = Jinja2Templates('app/presentation/api/endpoints/templates/html')


@router.get('/login')
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
    auth_service: AuthService = Depends(get_auth_service),
    user_repo: UserRepository = Depends(get_user_repository),
):
    """Вход и получение токена"""
    logger.info('start login')

    use_case = UserAuthenticationService(
        user_repo=user_repo,
        auth_service=auth_service)
    try:
        logger.info('try create token')
        token = await use_case.execute(
            email=form_data.username,
            password=form_data.password
        )
        logger.info(f'success token before create cookie {token}')

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
        logger.info('create response')
        return response
    except ValueError:
        return templates.TemplateResponse(
            name='login.html',
            context = {
                'request': request,
                'error': 'Неверный логин или пароль',
                'username': form_data.username
            },
            status_code=400
        )
