from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interfaces.logic_repository import ILogicRepository
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.repositories.logic_repository import LogicRepository


async def get_logic_repository(
    session: AsyncSession = Depends(get_db),
) -> ILogicRepository:
    return LogicRepository(session)
