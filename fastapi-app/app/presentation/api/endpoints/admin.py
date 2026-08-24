import datetime as dt
from functools import wraps
from typing import Any

import aiohttp
from fastapi import APIRouter, Form, HTTPException, Query, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

ADMIN_API_URL = "http://127.0.0.1:8001"
templates = Jinja2Templates("app/presentation/api/endpoints/templates/html")


async def delete_admin_api(path: str) -> None:
    status, _ = await request_admin_api("DELETE", path)
    if status == 204:
        return
    if status == 404:
        raise HTTPException(
            status_code=404,
            detail="Not found",
        )

    raise HTTPException(
        status_code=502,
        detail=f"Admin API returned status {status}",
    )


async def request_admin_api(
    method: str,
    path: str,
    **kwargs: Any,
) -> tuple[int, Any]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                f"{ADMIN_API_URL}{path}",
                **kwargs,
            ) as response:
                if response.status == 204:
                    return response.status, None
                if response.content_type == "application/json":
                    return response.status, await response.json()
                return response.status, await response.text()
    except aiohttp.ClientError as error:
        raise HTTPException(
            status_code=502,
            detail="admin API is unavailable",
        ) from error


async def get_admin_data(method: str, path: str, params: dict[str, Any]) -> Any:
    status, data = await request_admin_api(method, path, params=params)
    if status != 200:
        raise HTTPException(status_code=502, detail="admin API request failed")
    return data


def check_token(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        token = request.cookies.get("admin_access_token")
        if not token:
            return RedirectResponse("/admin/login", status_code=303)
        status, _ = await request_admin_api(
            "GET",
            "/admin/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        if status == 401:
            return RedirectResponse("/admin/login", status_code=303)
        if status != 204:
            return Response("internal server error", status_code=500)
        return await func(request, *args, **kwargs)

    return wrapper


@router.get("/admin/login")
async def register_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login_admin.html",
    )


@router.post("/admin/login")
async def register_check(
    login: str = Form(...),
    password: str = Form(...),
):
    status, data = await request_admin_api(
        "POST",
        "/admin/login",
        json={"login": login, "password": password},
    )
    if status != 200 or not isinstance(data, dict):
        return Response(content="invalid credentials", status_code=401)

    token = data.get("access_token")
    if not token:
        return Response(content="internal server error", status_code=502)

    response = RedirectResponse("/admin", status_code=303)

    response.set_cookie(
        key="admin_access_token", value=token, httponly=True, samesite="lax"
    )
    return response


@router.get("/admin")
@check_token
async def admin(
    request: Request,
    selected_date: dt.date | None = Query(None, alias="date"),
):
    date = (selected_date or dt.datetime.now().date()).isoformat()
    statistics = await get_admin_data("GET", "/admin/statistics", {"date": date})
    return templates.TemplateResponse(
        request=request,
        name="admin/admin.html",
        context={
            "articles_today": statistics["articles_today"],
            "users_today": statistics["users_today"],
            "quantity_users": statistics["quantity_users"]["Value"]
            if statistics["quantity_users"]["Err"].strip() == ""
            else statistics["quantity_users"]["Err"],
            "quantity_articles": statistics["quantity_articles"]["Value"]
            if statistics["quantity_articles"]["Err"].strip() == ""
            else statistics["quantity_articles"]["Err"],
        },
    )


@router.get("/admin/users")
@check_token
async def users_menu(
    request: Request,
    user_id: int | None = Query(None, alias="id"),
    email: str | None = Query(None),
    username: str | None = Query(None),
):
    params = {
        key: value
        for key, value in {
            "user_id": user_id,
            "email": email,
            "username": username,
        }.items()
        if value not in (None, "")
    }
    users = await get_admin_data("GET", "/admin/users", params)
    return templates.TemplateResponse(
        request=request,
        name="admin/admin_users.html",
        context={"users": users},
    )


@router.post("/admin/users/{user_id}")
@check_token
async def user_delete(
    request: Request,
    user_id: int,
):
    await delete_admin_api(f"/admin/users/{user_id}")
    return RedirectResponse("/admin/users", status_code=303)


@router.get("/admin/articles")
@check_token
async def articles_menu(
    request: Request,
    user_id: int | None = Query(None),
    title: str | None = Query(None),
    article_id: int | None = Query(None),
):
    params = {
        key: value
        for key, value in {
            "article_id": article_id,
            "title": title,
            "user_id": user_id,
        }.items()
        if value not in (None, "")
    }
    articles = await get_admin_data("GET", "/admin/articles", params)
    return templates.TemplateResponse(
        request=request,
        name="admin/admin_articles.html",
        context={"articles": articles},
    )


@router.post("/admin/articles/{article_id}")
@check_token
async def article_delete(
    request: Request,
    article_id: int,
):
    await delete_admin_api(f"/admin/articles/{article_id}")
    return RedirectResponse("/admin/articles", status_code=303)


@router.get("/admin/comments")
@check_token
async def comments_menu(
    request: Request,
    user_id: int | None = Query(None),
    article_id: int | None = Query(None),
    public_date: dt.date | None = Query(None),
):
    params = {
        key: value
        for key, value in {
            "article_id": article_id,
            "public_date": public_date.isoformat() if public_date else None,
            "user_id": user_id,
        }.items()
        if value not in (None, "")
    }
    comments = await get_admin_data("GET", "/admin/comments", params)
    return templates.TemplateResponse(
        request=request,
        name="admin/admin_comments.html",
        context={"comments": comments},
    )


@router.post("/admin/comments/{comment_id}")
@check_token
async def comment_delete(
    request: Request,
    comment_id: int,
):
    await delete_admin_api(f"/admin/comments/{comment_id}")
    return RedirectResponse("/admin/comments", status_code=303)
