from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import aiohttp

router = APIRouter()

templates = Jinja2Templates('app/presentation/api/endpoints/templates/html')

@router.get("/admin/register")
async def admin_register_form(request: Request):
    return templates.TemplateResponse( 
        'register_admin.html',
        context={
            "request": request
        })

@router.post('/admin/register/check')
async def admin_register_check(
    login: str = Form(...),
    password: str = Form(...)
):
    async with aiohttp.ClientSession() as session:
        response = await session.post(
            "http://127.0.0.1:8001/admin/register",
            json={
                "login": login,
                "password": password
            }
        )
        data = await response.json()

        token = data['access_token']
    
    response = RedirectResponse("/admin/main", status_code=303)

    response.set_cookie(
        key="admin_access_token",
        value=token,
        httponly=True,
        samesite="lax"
    )
    return response

@router.get("/admin/main")
async def admin_users(request: Request):
    token = request.cookies["admin_access_token"]
    async with aiohttp.ClientSession() as session:
        response = await session.get(
            "http://127.0.0.1:8001/admin/info",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )
    return response.json()
            