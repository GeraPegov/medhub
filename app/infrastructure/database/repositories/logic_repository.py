from datetime import datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interfaces.logic_repository import ILogicRepository
from app.infrastructure.database.models.user import User


class LogicRepository(ILogicRepository):
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session

    async def check_limited(self, user_id: int) -> bool:
        quanity_publication = (await self.session.execute(
            select(User)
            .where(User.id==user_id)
        )).scalar_one()
        print(f'hello it is quanity_publication {quanity_publication}')
        if quanity_publication.publication_limit < 2:
            if quanity_publication.publication_limit == 0:
                update_orm = await self.session.execute(
                    update(User)
                    .where(User.id==user_id)
                    .values(first_publication_date=datetime.now(),
                            publication_limit=User.publication_limit+1)
                    .returning(User.publication_limit)
                )
                print(f'hello tthis is how end quanity publication 1 {update_orm.scalar_one_or_none()}')
                return True
            else:
                update_orm = await self.session.execute(
                    update(User)
                    .where(User.id==user_id)
                    .values(publication_limit=User.publication_limit+1)
                    .returning(User.publication_limit)
                )
                print(f'hello tthis is how end quanity publication 2 {update_orm.scalar_one_or_none()}')
                return True
        else:
            time_add = timedelta(days=1)
            if quanity_publication.first_publication_date < quanity_publication.first_publication_date + time_add:
                return False
            else:
                update_orm = await self.session.execute(
                    update(User)
                    .where(User.id==user_id)
                    .values(publication_limit=1,
                            first_publication_date=datetime.now())
                    .returning(User.first_publication_date)
                )
                print(f'hello this is how end quanity publication 3 {update_orm.scalar_one_or_none()}')
                return True
