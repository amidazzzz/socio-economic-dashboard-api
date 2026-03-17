from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.indicator import Indicator
from app.model.unit import Unit


async def load_indicators(session: AsyncSession) -> None:
    # units
    person_unit = (
        await session.execute(
            select(Unit).where(Unit.code == "PERSON")
        )
    ).scalar_one()

    percent_unit = (
        await session.execute(
            select(Unit).where(Unit.code == "PERCENT")
        )
    ).scalar_one()

    indicators_data = [
        {
            "code": "POPULATION_TOTAL",
            "name": "Численность населения",
            "description": "Численность постоянного населения на 1 января",
            "unit_id": person_unit.id,
        },
        {
            "code": "UNEMPLOYMENT_RATE",
            "name": "Уровень безработицы",
            "description": "Уровень безработицы по методологии МОТ",
            "unit_id": percent_unit.id,
        },
    ]

    created = 0

    for data in indicators_data:
        exists = (
            await session.execute(
                select(Indicator).where(Indicator.code == data["code"])
            )
        ).scalar_one_or_none()

        if exists:
            continue

        session.add(Indicator(**data))
        created += 1

    await session.commit()

    print(f"[ETL] Добавлено новых индикаторов: {created}")
