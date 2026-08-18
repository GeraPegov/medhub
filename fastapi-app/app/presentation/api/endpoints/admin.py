from datetime import datetime
from functools import wraps

import aiohttp
from fastapi import APIRouter, Form, Query, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates('app/presentation/api/endpoints/templates/html')

def check_token(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        token = request.cookies.get("admin_access_token")
        if not token:
            return RedirectResponse("/admin/login", status_code=303)
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                "http://127.0.0.1:8001/admin/me",
                headers={
                    "Authorization": f"Bearer {token}"
                }
            )
        if response.status == 401:
            return RedirectResponse('/admin/login', status_code=303)
        if response.status != 204:
            return Response(
                'internal server error',
                status_code=500
            )
        return await func(request, *args, **kwargs)
    return wrapper

@router.get("/admin/login")
async def admin_register_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='login_admin.html')


@router.post('/admin/login')
async def admin_register_check(
    login: str = Form(...),
    password: str = Form(...)
):
    async with aiohttp.ClientSession() as session:
        response = await session.post(
            "http://127.0.0.1:8001/admin/login",
            json={
                "login": login,
                "password": password
            }
        )
        data = await response.json()

        token = data['access_token']
        if response.status != 200:
            error_text = await response.text()
            print(error_text)

            return Response(
                content="internal server error",
                status_code=500
            )
    response = RedirectResponse("/admin", status_code=303)

    response.set_cookie(
        key="admin_access_token",
        value=token,
        httponly=True,
        samesite="lax"
    )
    return response


@router.get("/admin")
@check_token
async def admin_users(request: Request, date: str | None = Query(None)):
    if date == "" or date is None:
        date = datetime.now().date().isoformat()
    async with aiohttp.ClientSession() as session:
        response = await session.get("http://127.0.0.1:8001/admin/statistics", params={"date": date})
    statistics = await response.json()
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
        'articles_today': statistics['articles_today'],
        'users_today': statistics['users_today'],
        'quantity_users': statistics['quantity_users']['Value'] if statistics['quantity_users']['Err'].strip() == "" else statistics['quantity_users']['Err'],
        'quantity_articles': statistics['quantity_articles']['Value'] if statistics['quantity_articles']['Err'].strip() == "" else statistics['quantity_articles']['Err']
    })
