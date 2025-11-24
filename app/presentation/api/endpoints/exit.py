from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter()

@router.get('/exit')
async def exit(
):
    response = RedirectResponse(
            url='/',
            status_code=303
        )
    response.delete_cookie(
        key='access_token'
    )

    return response
