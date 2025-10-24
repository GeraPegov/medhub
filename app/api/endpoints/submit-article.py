from fastapi import APIRouter, Form, Depends
from h11 import Request

router = APIRouter()

@router.post('submit-article')
async def add_article_in_db(
    author: str = Form(),
    title: str = Form(),
    content: str = Form(),
    database,
    request: Request
):
    