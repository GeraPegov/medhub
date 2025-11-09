from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from app.domain.logging import logger
from app.application.services.login_user import LoginUserUseCase
from app.presentation.dependencies.auth import get_auth_service, get_user_repository

router = APIRouter()
templates = Jinja2Templates('app/presentation/api/endpoints/templates')


@router.get('/login')
def page_of_login(request: Request):
    return templates.TemplateResponse(
        'login.html',
        {'request': request}
    )

@router.post('/auth/login')
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service = Depends(get_auth_service),
    user_repo = Depends(get_user_repository)
):
    """Вход и получение токена"""
    logger.info(f'start LOGIN, form_data : {form_data}')
    use_case = LoginUserUseCase(
        user_repo=user_repo,
        auth_service=auth_service)
    logger.info(f'use case : {use_case}')
    try:
        token = await use_case.execute(
            email=form_data.username,
            password=form_data.password
        )
        return {'access_token': token, 'token_type': 'bearer'}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={'WWW-Authenticate': 'Bearer'}
        ) from None
