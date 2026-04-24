from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from app.etl.contracts import IndicatorValueRecord
from app.model import Indicator, IndicatorValue, Region


async def load_indicator_values(
    session: AsyncSession,
    indicator_code: str,
    records: list[IndicatorValueRecord],
) -> int:
    result = await session.execute(
        select(Indicator).where(Indicator.code == indicator_code)
    )
    indicator = result.scalar_one()

    result = await session.execute(select(Region))
    regions = {r.name: r.id for r in result.scalars().all()}

    unique_records: dict[tuple[int, int, str], IndicatorValueRecord] = {}

    for rec in records:
        region_id = regions.get(rec["region_name"])
        if not region_id:
            continue

        key = (region_id, rec["year"], rec["period"])
        unique_records[key] = rec

    synced = 0
    for (region_id, year, period), rec in unique_records.items():
        stmt = (
            insert(IndicatorValue)
            .values(
                indicator_id=indicator.id,
                region_id=region_id,
                year=year,
                period=period,
                value=rec["value"],
                source=rec["source"],
            )
            .on_conflict_do_update(
                constraint="uq_indicator_region_year",
                set_={
                    "value": rec["value"],
                    "source": rec["source"],
                },
            )
        )
        await session.execute(stmt)
        synced += 1

    await session.commit()

    print(f"[ETL] Синхронизировано значений: {synced}")
    return synced
