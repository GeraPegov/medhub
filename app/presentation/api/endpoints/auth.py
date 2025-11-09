from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from app.application.dto.articleAuth_dto import ArticleAuthDTO
from app.application.services.login_user import LoginUserUseCase
from app.application.services.register_user import RegisterUserUseCase
from app.domain.logging import logger

# from presentation.api.schemas.user_schema import UserCreate, Token
from app.presentation.dependencies.auth import get_auth_service, get_user_repository
from app.presentation.dependencies.parse_user import parse_auth_form

router = APIRouter()

templates = Jinja2Templates('app/api/endpoints/templates')

@router.get('/home/register')
async def page_of_register(
    request: Request
):
    logger.info('start of form register')
    return templates.TemplateResponse(
        'register.html',
        {'request': request}
    )

# @router.post('/auth/register')
# async def main_register(
#     request: Request,
#     dto: ArticleRegisterDTO = Depends(parse_register_form),
#     manager: ArticleManager = Depends(get_article_manager)
# ):
#     await manager.log_in(dto)

@router.post('/register')
async def register(
    user_data: ArticleAuthDTO = Depends(parse_auth_form),
    auth_service = Depends(get_auth_service),
    user_repo = Depends(get_user_repository)
):
    logger.info(f'start endpoint of register with date {user_data.email}')
    """Регистрация пользователя"""
    use_case = RegisterUserUseCase(user_repo, auth_service)
    logger.info('start use_case in endpoint register')
    try:
        user = await use_case.execute(
            email=user_data.email,
            password=user_data.password,
            username=user_data.username
        )
        return {'message': 'Успешная регистрация', 'user_id': user.id}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post('/login', response_model="Token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service = Depends(get_auth_service),
    user_repo = Depends(get_user_repository)
):
    """Вход и получение токена"""
    use_case = LoginUserUseCase(user_repo, auth_service)

    try:
        token = use_case.execute(
            email=form_data.username,
            password=form_data.password
        )
        return {'access_token': token, 'token_type': 'bearer'}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={'WWW-Authenticate': 'Bearer'}
        )
