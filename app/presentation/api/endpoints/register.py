from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.application.dto.articleAuth_dto import ArticleAuthDTO
from app.application.services.register_user import UserRegistrationService
from app.domain.logging import logger
from app.presentation.dependencies.auth import get_auth_registration
from app.presentation.dependencies.parse_user import parse_auth_form

router = APIRouter()

templates = Jinja2Templates('app/presentation/api/endpoints/templates/html')

@router.get('/register')
async def page_of_register(
    request: Request
):
    logger.info('start of form register')
    return templates.TemplateResponse(
        'register.html',
        {'request': request}
    )

@router.post('/auth/register')
async def register(
    request: Request,
    user_data: ArticleAuthDTO = Depends(parse_auth_form),
    registration_service: UserRegistrationService = Depends(get_auth_registration)
):
    user = await registration_service.execute(
        email=user_data.email,
        password=user_data.password,
        username=user_data.username,
        nickname=user_data.nickname
    )

    if not user:
        return templates.TemplateResponse(
        'register.html',
        {
        'request': request,
        'error': 'Email уже зарегестрирован'
        }
    )
    response = RedirectResponse(
        url='/login',
        status_code=303
    )
    return response

