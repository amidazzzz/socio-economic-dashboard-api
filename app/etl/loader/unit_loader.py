from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from app.model.unit import Unit


async def load_units(session: AsyncSession) -> None:
    units = [
        {"code": "PERSON", "name": "человек"},
        {"code": "PERCENT", "name": "процент"},
    ]

    for u in units:
        stmt = insert(Unit).values(**u).on_conflict_do_nothing(
            index_elements=["code"]
        )
        await session.execute(stmt)

    await session.commit()
    print("[ETL] Units synced")