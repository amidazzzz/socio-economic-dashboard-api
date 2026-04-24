from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model import Indicator, Region
from app.model.indicator_value import IndicatorValue


class IndicatorValueRepository:
    @staticmethod
    async def get_analytics_rows(
        session: AsyncSession,
        indicator_codes: list[str],
        region_id: int | None = None,
        start_year: int | None = None,
        end_year: int | None = None,
    ):
        stmt = (
            select(
                Region.id.label("region_id"),
                Region.name.label("region_name"),
                Indicator.code.label("indicator_code"),
                IndicatorValue.year.label("year"),
                IndicatorValue.value.label("value"),
            )
            .join(IndicatorValue, IndicatorValue.region_id == Region.id)
            .join(Indicator, Indicator.id == IndicatorValue.indicator_id)
            .where(
                Region.parent_id.is_(None),
                Indicator.code.in_(indicator_codes),
                IndicatorValue.period == "year",
            )
            .order_by(Region.name, IndicatorValue.year, Indicator.code)
        )

        if region_id is not None:
            stmt = stmt.where(Region.id == region_id)
        if start_year is not None:
            stmt = stmt.where(IndicatorValue.year >= start_year)
        if end_year is not None:
            stmt = stmt.where(IndicatorValue.year <= end_year)

        result = await session.execute(stmt)
        return result.all()
