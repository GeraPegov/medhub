from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
import aiohttp

router = APIRouter()

templates = Jinja2Templates('app/presentation/api/endpoints/templates/html')

@router.get("/admin/register")
async def admin_register_form(request: Request):
    return templates.TemplateResponse( 
        'admin.html',
        context={
            "request": request
        })

@router.post('/admin/register/check')
async def admin_register_check(
    login: str = Form(...),
    password: str = Form(...)
):
    async with aiohttp.ClientSession() as session:
        await session.post(
            f"http://127.0.0.1:8001/admin/register",
            json={
                "login": login,
                "password": password
            }
        )
            