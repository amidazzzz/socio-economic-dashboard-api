from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from app.model.unit import Unit


async def load_units(session: AsyncSession) -> int:
    units = [
        {"code": "PERSON", "name": "человек"},
        {"code": "PERCENT", "name": "процент"},
        {"code": "THOUSAND_RUBLES", "name": "тыс. рублей"},
        {"code": "PER_10000_PERSONS", "name": "на 10 тыс. человек"},
    ]

    for u in units:
        stmt = insert(Unit).values(**u).on_conflict_do_nothing(
            index_elements=["code"]
        )
        await session.execute(stmt)

    await session.commit()
    print("[ETL] Units synced")
    return len(units)
