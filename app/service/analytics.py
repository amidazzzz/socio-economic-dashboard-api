from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.indicator_value_repository import IndicatorValueRepository
import math

POPULATION_INDICATOR_ID = 1
UNEMPLOYMENT_INDICATOR_ID = 3

class AnalyticsService:

    @staticmethod
    async def get_region_year_analytics(
        session: AsyncSession,
        region_id: int,
    ) -> list[dict]:
        """
        Возвращает аналитику по региону:
        [
          {
            "year": 2020,
            "population": 1234567,
            "unemployment_rate": 4.5
          },
          ...
        ]
        """

        rows = await IndicatorValueRepository.get_by_region_and_indicators(
            session=session,
            region_id=region_id,
            indicator_ids=[
                POPULATION_INDICATOR_ID,
                UNEMPLOYMENT_INDICATOR_ID,
            ],
        )

        data_by_year: dict[int, dict] = defaultdict(
            lambda: {
                "population": None,
                "unemployment_rate": None,
            }
        )

        for row in rows:
            if row.indicator_id == POPULATION_INDICATOR_ID:
                data_by_year[row.year]["population"] = row.value

            elif row.indicator_id == UNEMPLOYMENT_INDICATOR_ID:
                data_by_year[row.year]["unemployment_rate"] = row.value

        # приводим к списку
        result = []
        for year in sorted(data_by_year.keys()):
            result.append(
                {
                    "year": year,
                    **data_by_year[year],
                }
            )

        return result

    # корреляция Пирсона
    @staticmethod
    async def get_population_unemployment_correlation(
            session: AsyncSession,
            region_id: int,
    ) -> float | None:
        rows = await IndicatorValueRepository.get_by_region_and_indicators(
            session=session,
            region_id=region_id,
            indicator_ids=[
                POPULATION_INDICATOR_ID,
                UNEMPLOYMENT_INDICATOR_ID,
            ],
        )

        population_by_year = {}
        unemployment_by_year = {}

        for row in rows:
            if row.indicator_id == POPULATION_INDICATOR_ID:
                population_by_year[row.year] = row.value
            elif row.indicator_id == UNEMPLOYMENT_INDICATOR_ID:
                unemployment_by_year[row.year] = row.value

        common_years = sorted(
            set(population_by_year.keys())
            & set(unemployment_by_year.keys())
        )

        if len(common_years) < 2:
            return None

        x = [population_by_year[y] for y in common_years]
        y = [unemployment_by_year[y] for y in common_years]

        mean_x = sum(x) / len(x)
        mean_y = sum(y) / len(y)

        numerator = sum(
            (xi - mean_x) * (yi - mean_y)
            for xi, yi in zip(x, y)
        )

        denominator_x = math.sqrt(
            sum((xi - mean_x) ** 2 for xi in x)
        )
        denominator_y = math.sqrt(
            sum((yi - mean_y) ** 2 for yi in y)
        )

        if denominator_x == 0 or denominator_y == 0:
            return None

        return float(numerator) / (denominator_x * denominator_y)

    @staticmethod
    async def get_top_regions_by_unemployment(
        session: AsyncSession,
        year: int,
        limit: int = 10,
    ):
        rows = await IndicatorValueRepository.get_top_regions_by_unemployment(
            session=session,
            year=year,
            limit=limit,
        )

        return [
            {
                "region_id": r.id,
                "region_name": r.name,
                "unemployment_rate": r.unemployment_rate,
            }
            for r in rows
        ]

    @staticmethod
    def calculate_growth_rates(
            values_by_year: dict[int, float]
    ) -> dict[int, float | None]:
        """
        Возвращает темпы роста по годам (%)
        """
        years = sorted(values_by_year.keys())
        growth = {}

        for i, year in enumerate(years):
            if i == 0:
                growth[year] = None
                continue

            prev_year = years[i - 1]
            prev_value = values_by_year[prev_year]
            current_value = values_by_year[year]

            if prev_value == 0:
                growth[year] = None
            else:
                growth[year] = (
                                       (current_value - prev_value) / prev_value
                               ) * 100

        return growth

    @staticmethod
    async def get_region_growth_rates(
            session,
            region_id: int,
    ):
        rows = await IndicatorValueRepository.get_by_region_and_indicators(
            session=session,
            region_id=region_id,
            indicator_ids=[
                POPULATION_INDICATOR_ID,
                UNEMPLOYMENT_INDICATOR_ID,
            ],
        )

        population = {}
        unemployment = {}

        for row in rows:
            if row.indicator_id == POPULATION_INDICATOR_ID:
                population[row.year] = row.value
            elif row.indicator_id == UNEMPLOYMENT_INDICATOR_ID:
                unemployment[row.year] = row.value

        population_growth = AnalyticsService.calculate_growth_rates(population)
        unemployment_growth = AnalyticsService.calculate_growth_rates(unemployment)

        result = []
        for year in sorted(set(population.keys()) | set(unemployment.keys())):
            result.append({
                "year": year,
                "population_growth_pct": population_growth.get(year),
                "unemployment_growth_pct": unemployment_growth.get(year),
            })

        return result