from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.model import Indicator, Region
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
    async def get_analytics_dataset(
        session: AsyncSession,
        region_id: int | None = None,
        start_year: int | None = None,
        end_year: int | None = None,
    ):
        population_value = aliased(IndicatorValue)
        unemployment_value = aliased(IndicatorValue)
        population_indicator = aliased(Indicator)
        unemployment_indicator = aliased(Indicator)

        stmt = (
            select(
                Region.id.label("region_id"),
                Region.name.label("region_name"),
                population_value.year.label("year"),
                population_value.value.label("population"),
                unemployment_value.value.label("unemployment_rate"),
            )
            .join(
                population_value,
                and_(
                    population_value.region_id == Region.id,
                    population_value.period == "year",
                ),
            )
            .join(
                population_indicator,
                and_(
                    population_indicator.id == population_value.indicator_id,
                    population_indicator.code == "POPULATION_TOTAL",
                ),
            )
            .join(
                unemployment_value,
                and_(
                    unemployment_value.region_id == Region.id,
                    unemployment_value.year == population_value.year,
                    unemployment_value.period == "year",
                ),
            )
            .join(
                unemployment_indicator,
                and_(
                    unemployment_indicator.id == unemployment_value.indicator_id,
                    unemployment_indicator.code == "UNEMPLOYMENT_RATE",
                ),
            )
            .where(
                Region.parent_id.is_(None),
            )
            .order_by(Region.name, population_value.year)
        )

        if region_id is not None:
            stmt = stmt.where(Region.id == region_id)
        if start_year is not None:
            stmt = stmt.where(population_value.year >= start_year)
        if end_year is not None:
            stmt = stmt.where(population_value.year <= end_year)

        result = await session.execute(stmt)
        return result.all()
