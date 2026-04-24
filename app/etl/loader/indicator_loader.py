from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.indicator import Indicator
from app.model.unit import Unit


async def load_indicators(session: AsyncSession) -> int:
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

    thousand_rubles_unit = (
        await session.execute(
            select(Unit).where(Unit.code == "THOUSAND_RUBLES")
        )
    ).scalar_one()

    per_10000_persons_unit = (
        await session.execute(
            select(Unit).where(Unit.code == "PER_10000_PERSONS")
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
        {
            "code": "NATURAL_INCREASE",
            "name": "Естественный прирост населения",
            "description": "Естественный прирост населения, человек, значение показателя за год",
            "unit_id": person_unit.id,
        },
        {
            "code": "AVERAGE_SALARY_REAL_INDEX",
            "name": "Индекс реальной среднемесячной заработной платы",
            "description": "Уровень реальной среднемесячной заработной платы, процент, значение показателя за год",
            "unit_id": percent_unit.id,
        },
        {
            "code": "MIGRATION_BALANCE_RATE",
            "name": "Коэффициент миграционного прироста",
            "description": "Коэффициент миграционного прироста на 10 тыс. человек, значение показателя за год",
            "unit_id": per_10000_persons_unit.id,
        },
        {
            "code": "VRP_TOTAL",
            "name": "Валовой региональный продукт",
            "description": "Валовой региональный продукт в основных ценах, значение показателя за год",
            "unit_id": thousand_rubles_unit.id,
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
    return created
