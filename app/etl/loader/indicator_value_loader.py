from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.model import Indicator, IndicatorValue, Region


async def load_indicator_values(
    session: AsyncSession,
    indicator_code: str,
    records: list[dict],
) -> None:

    # получаем indicator
    result = await session.execute(
        select(Indicator).where(Indicator.code == indicator_code)
    )
    indicator = result.scalar_one()

    # заранее получаем все регионы в dict (ОЧЕНЬ важно для perf)
    result = await session.execute(select(Region))
    regions = {r.name: r.id for r in result.scalars().all()}

    # чистим старые значения показателя
    await session.execute(
        delete(IndicatorValue).where(
            IndicatorValue.indicator_id == indicator.id
        )
    )

    values = []

    for rec in records:
        region_id = regions.get(rec["region_name"])
        if not region_id:
            continue  # если вдруг название не совпало

        values.append(
            IndicatorValue(
                indicator_id=indicator.id,
                region_id=region_id,
                year=rec["year"],
                period=rec["period"],
                value=rec["value"],
                source=rec["source"],
            )
        )

    session.add_all(values)
    await session.commit()

    print(f"[ETL] Загружено значений: {len(values)}")
