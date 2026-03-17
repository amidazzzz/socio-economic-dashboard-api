from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model import Region
from app.model.indicator_value import IndicatorValue


class IndicatorValueRepository:

    @staticmethod
    async def get_by_region_and_indicators(
        session: AsyncSession,
        region_id: int,
        indicator_ids: list[int],
    ):
        stmt = (
            select(IndicatorValue)
            .where(
                IndicatorValue.region_id == region_id,
                IndicatorValue.indicator_id.in_(indicator_ids),
                IndicatorValue.period == "year",
            )
            .order_by(IndicatorValue.year)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_top_regions_by_unemployment(
        session,
        year: int,
        limit: int = 10,
    ):
        stmt = (
            select(
                Region.id,
                Region.name,
                IndicatorValue.value.label("unemployment_rate"),
            )
            .join(IndicatorValue, IndicatorValue.region_id == Region.id)
            .where(
                IndicatorValue.indicator_id == 3,
                IndicatorValue.year == year,
                IndicatorValue.period == "year",
            )
            .order_by(IndicatorValue.value.desc())
            .limit(limit)
        )

        result = await session.execute(stmt)
        return result.all()
