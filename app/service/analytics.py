from collections import defaultdict
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.indicator_value_repository import IndicatorValueRepository


class AnalyticsService:
    @staticmethod
    def _to_float(value: Decimal | float | int) -> float:
        return float(value)

    @staticmethod
    async def get_analytics_dataset(
        session: AsyncSession,
        region_id: int | None = None,
        start_year: int | None = None,
        end_year: int | None = None,
    ) -> list[dict]:
        rows = await IndicatorValueRepository.get_analytics_dataset(
            session=session,
            region_id=region_id,
            start_year=start_year,
            end_year=end_year,
        )

        return [
            {
                "region_id": row.region_id,
                "region_name": row.region_name,
                "year": row.year,
                "population": AnalyticsService._to_float(row.population),
                "unemployment_rate": AnalyticsService._to_float(row.unemployment_rate),
            }
            for row in rows
        ]

    @staticmethod
    async def get_region_year_analytics(
        session: AsyncSession,
        region_id: int,
    ) -> list[dict]:
        rows = await AnalyticsService.get_analytics_dataset(
            session=session,
            region_id=region_id,
        )

        return [
            {
                "year": row["year"],
                "population": row["population"],
                "unemployment_rate": row["unemployment_rate"],
            }
            for row in rows
        ]

    @staticmethod
    def _calculate_population_growth(
        current_population: float,
        previous_population: float,
    ) -> float | None:
        if previous_population == 0:
            return None
        return (current_population - previous_population) / previous_population

    @staticmethod
    def _build_region_metrics(rows: list[dict]) -> list[dict]:
        metrics: list[dict] = []
        previous_row: dict | None = None

        for row in sorted(rows, key=lambda item: item["year"]):
            population_growth_rate = None
            unemployment_delta = None

            if previous_row and row["year"] == previous_row["year"] + 1:
                population_growth_rate = AnalyticsService._calculate_population_growth(
                    current_population=row["population"],
                    previous_population=previous_row["population"],
                )
                unemployment_delta = (
                    row["unemployment_rate"] - previous_row["unemployment_rate"]
                )

            metrics.append(
                {
                    "year": row["year"],
                    "population_growth_rate": population_growth_rate,
                    "unemployment_delta": unemployment_delta,
                }
            )
            previous_row = row

        return metrics

    @staticmethod
    async def get_region_growth_metrics(
        session: AsyncSession,
        region_id: int,
    ) -> list[dict]:
        rows = await AnalyticsService.get_analytics_dataset(
            session=session,
            region_id=region_id,
        )
        return AnalyticsService._build_region_metrics(rows)

    @staticmethod
    async def get_top_regions_by_low_unemployment(
        session: AsyncSession,
        year: int,
        limit: int = 10,
    ) -> list[dict]:
        rows = await AnalyticsService.get_analytics_dataset(
            session=session,
            start_year=year,
            end_year=year,
        )

        ranked_rows = sorted(rows, key=lambda row: (row["unemployment_rate"], row["region_name"]))
        return ranked_rows[:limit]

    @staticmethod
    async def get_top_regions_by_population_growth(
        session: AsyncSession,
        year: int,
        limit: int = 10,
    ) -> list[dict]:
        rows = await AnalyticsService.get_analytics_dataset(
            session=session,
            start_year=year - 1,
            end_year=year,
        )

        rows_by_region: dict[int, list[dict]] = defaultdict(list)
        for row in rows:
            rows_by_region[row["region_id"]].append(row)

        ranked_rows: list[dict] = []
        for region_rows in rows_by_region.values():
            metrics = AnalyticsService._build_region_metrics(region_rows)
            metric = next((item for item in metrics if item["year"] == year), None)
            dataset_row = next((item for item in region_rows if item["year"] == year), None)

            if not metric or metric["population_growth_rate"] is None or not dataset_row:
                continue

            ranked_rows.append(
                {
                    "region_id": dataset_row["region_id"],
                    "region_name": dataset_row["region_name"],
                    "year": year,
                    "population_growth_rate": metric["population_growth_rate"],
                }
            )

        ranked_rows.sort(
            key=lambda row: (-row["population_growth_rate"], row["region_name"])
        )
        return ranked_rows[:limit]

    @staticmethod
    async def get_regions_with_largest_unemployment_decline(
        session: AsyncSession,
        year: int,
        limit: int = 10,
    ) -> list[dict]:
        rows = await AnalyticsService.get_analytics_dataset(
            session=session,
            start_year=year - 1,
            end_year=year,
        )

        rows_by_region: dict[int, list[dict]] = defaultdict(list)
        for row in rows:
            rows_by_region[row["region_id"]].append(row)

        ranked_rows: list[dict] = []
        for region_rows in rows_by_region.values():
            metrics = AnalyticsService._build_region_metrics(region_rows)
            metric = next((item for item in metrics if item["year"] == year), None)
            dataset_row = next((item for item in region_rows if item["year"] == year), None)

            if not metric or metric["unemployment_delta"] is None or not dataset_row:
                continue

            ranked_rows.append(
                {
                    "region_id": dataset_row["region_id"],
                    "region_name": dataset_row["region_name"],
                    "year": year,
                    "unemployment_delta": metric["unemployment_delta"],
                }
            )

        ranked_rows.sort(key=lambda row: (row["unemployment_delta"], row["region_name"]))
        return ranked_rows[:limit]

    @staticmethod
    async def get_population_unemployment_correlation(
        session: AsyncSession,
        region_id: int,
    ) -> float | None:
        rows = await AnalyticsService.get_analytics_dataset(
            session=session,
            region_id=region_id,
        )

        if len(rows) < 2:
            return None

        population_values = [row["population"] for row in rows]
        unemployment_values = [row["unemployment_rate"] for row in rows]

        mean_population = sum(population_values) / len(population_values)
        mean_unemployment = sum(unemployment_values) / len(unemployment_values)

        numerator = sum(
            (population - mean_population) * (unemployment - mean_unemployment)
            for population, unemployment in zip(population_values, unemployment_values)
        )
        population_denominator = sum(
            (population - mean_population) ** 2 for population in population_values
        ) ** 0.5
        unemployment_denominator = sum(
            (unemployment - mean_unemployment) ** 2
            for unemployment in unemployment_values
        ) ** 0.5

        if population_denominator == 0 or unemployment_denominator == 0:
            return None

        return numerator / (population_denominator * unemployment_denominator)
