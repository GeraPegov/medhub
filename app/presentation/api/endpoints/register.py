from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates

from app.application.dto.articleAuth_dto import ArticleAuthDTO
from app.application.services.register_user import UserRegistrationService
from app.domain.logging import logger

# from presentation.api.schemas.user_schema import UserCreate, Token
from app.presentation.dependencies.auth import get_auth_service, get_user_repository
from app.presentation.dependencies.parse_user import parse_auth_form

router = APIRouter()

templates = Jinja2Templates('app/presentation/api/endpoints/templates')

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
    user_data: ArticleAuthDTO = Depends(parse_auth_form),
    auth_service = Depends(get_auth_service),
    user_repo = Depends(get_user_repository)
):
    logger.info(f'start endpoint of register with date {user_data.email}')
    """Регистрация пользователя"""
    use_case = UserRegistrationService(user_repo, auth_service)
    logger.info('start use_case in endpoint register')
    try:
        user = await use_case.execute(
            email=user_data.email,
            password=user_data.password,
            username=user_data.username
        )
        return {'message': 'Успешная регистрация', 'user_id': user.id}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)) from None

