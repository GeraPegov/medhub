from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from app.application.services.article_manager import ArticleService
from app.application.services.login_user import UserAuthenticationService
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.security.auth_service import AuthService
from app.presentation.dependencies.articles_dependencies import get_article_manager
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
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
    user_repo: UserRepository = Depends(get_user_repository),
    manager: ArticleService = Depends(get_article_manager)
):
    """Вход и получение токена"""
    use_case = UserAuthenticationService(
        user_repo=user_repo,
        auth_service=auth_service)
    try:
        token = await use_case.execute(
            email=form_data.username,
            password=form_data.password
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
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={'WWW-Authenticate': 'Bearer'}
        ) from None
