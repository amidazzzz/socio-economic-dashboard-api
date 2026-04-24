from collections import defaultdict
from decimal import Decimal
from math import sqrt

from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.indicator_value_repository import IndicatorValueRepository


class AnalyticsService:
    INDICATOR_FIELD_MAP = {
        "POPULATION_TOTAL": "population",
        "UNEMPLOYMENT_RATE": "unemployment_rate",
        "NATURAL_INCREASE": "natural_increase",
        "MIGRATION_BALANCE_RATE": "migration_balance",
        "AVERAGE_SALARY_REAL_INDEX": "average_salary",
        "VRP_TOTAL": "vrp",
    }

    DATASET_FIELDS = (
        "population",
        "unemployment_rate",
        "natural_increase",
        "migration_balance",
        "average_salary",
        "vrp",
    )

    @staticmethod
    def _to_float(value: Decimal | float | int) -> float:
        return float(value)

    @staticmethod
    def _empty_dataset_row(region_id: int, region_name: str, year: int) -> dict:
        row = {
            "region_id": region_id,
            "region_name": region_name,
            "year": year,
        }
        for field in AnalyticsService.DATASET_FIELDS:
            row[field] = None
        return row

    @staticmethod
    async def get_analytics_dataset(
        session: AsyncSession,
        region_id: int | None = None,
        start_year: int | None = None,
        end_year: int | None = None,
    ) -> list[dict]:
        rows = await IndicatorValueRepository.get_analytics_rows(
            session=session,
            indicator_codes=list(AnalyticsService.INDICATOR_FIELD_MAP.keys()),
            region_id=region_id,
            start_year=start_year,
            end_year=end_year,
        )

        data_by_key: dict[tuple[int, int], dict] = {}
        for row in rows:
            key = (row.region_id, row.year)
            if key not in data_by_key:
                data_by_key[key] = AnalyticsService._empty_dataset_row(
                    region_id=row.region_id,
                    region_name=row.region_name,
                    year=row.year,
                )

            field_name = AnalyticsService.INDICATOR_FIELD_MAP[row.indicator_code]
            data_by_key[key][field_name] = AnalyticsService._to_float(row.value)

        return sorted(
            data_by_key.values(),
            key=lambda item: (item["region_name"], item["year"]),
        )

    @staticmethod
    async def get_region_year_analytics(
        session: AsyncSession,
        region_id: int,
    ) -> list[dict]:
        return await AnalyticsService.get_analytics_dataset(
            session=session,
            region_id=region_id,
        )

    @staticmethod
    def _calculate_growth(current: float | None, previous: float | None) -> float | None:
        if current is None or previous in (None, 0):
            return None
        return (current - previous) / previous

    @staticmethod
    def _calculate_delta(current: float | None, previous: float | None) -> float | None:
        if current is None or previous is None:
            return None
        return current - previous

    @staticmethod
    def _safe_divide(numerator: float | None, denominator: float | None) -> float | None:
        if numerator is None or denominator in (None, 0):
            return None
        return numerator / denominator

    @staticmethod
    def _mean(values: list[float]) -> float | None:
        if not values:
            return None
        return sum(values) / len(values)

    @staticmethod
    def _std(values: list[float]) -> float | None:
        if len(values) < 2:
            return None
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        if variance == 0:
            return None
        return sqrt(variance)

    @staticmethod
    def _z_score(value: float | None, values: list[float]) -> float | None:
        if value is None:
            return None
        mean = AnalyticsService._mean(values)
        std = AnalyticsService._std(values)
        if mean is None or std is None:
            return None
        return (value - mean) / std

    @staticmethod
    def _minmax(value: float | None, values: list[float]) -> float | None:
        if value is None or not values:
            return None
        min_value = min(values)
        max_value = max(values)
        if min_value == max_value:
            return None
        return (value - min_value) / (max_value - min_value)

    @staticmethod
    def _moving_average(values: list[float | None], window: int = 3) -> list[float | None]:
        result: list[float | None] = []
        for index in range(len(values)):
            window_values = values[max(0, index - window + 1): index + 1]
            if len(window_values) < window or any(value is None for value in window_values):
                result.append(None)
                continue
            numeric_values = [float(value) for value in window_values if value is not None]
            result.append(sum(numeric_values) / window)
        return result

    @staticmethod
    def _pearson_correlation(x_values: list[float], y_values: list[float]) -> float | None:
        if len(x_values) != len(y_values) or len(x_values) < 2:
            return None

        mean_x = sum(x_values) / len(x_values)
        mean_y = sum(y_values) / len(y_values)
        numerator = sum(
            (x_value - mean_x) * (y_value - mean_y)
            for x_value, y_value in zip(x_values, y_values)
        )
        denominator_x = sqrt(sum((x_value - mean_x) ** 2 for x_value in x_values))
        denominator_y = sqrt(sum((y_value - mean_y) ** 2 for y_value in y_values))
        if denominator_x == 0 or denominator_y == 0:
            return None
        return numerator / (denominator_x * denominator_y)

    @staticmethod
    def _linear_regression(values_by_year: dict[int, float | None]) -> dict:
        filtered = [
            (year, value)
            for year, value in sorted(values_by_year.items())
            if value is not None
        ]
        if len(filtered) < 2:
            return {"slope": None, "intercept": None}

        x_values = [float(year) for year, _ in filtered]
        y_values = [float(value) for _, value in filtered]
        mean_x = sum(x_values) / len(x_values)
        mean_y = sum(y_values) / len(y_values)
        denominator = sum((x_value - mean_x) ** 2 for x_value in x_values)
        if denominator == 0:
            return {"slope": None, "intercept": None}

        slope = sum(
            (x_value - mean_x) * (y_value - mean_y)
            for x_value, y_value in zip(x_values, y_values)
        ) / denominator
        intercept = mean_y - slope * mean_x
        return {"slope": slope, "intercept": intercept}

    @staticmethod
    def _build_region_metrics(rows: list[dict]) -> list[dict]:
        ordered_rows = sorted(rows, key=lambda item: item["year"])

        population_ma = AnalyticsService._moving_average([row["population"] for row in ordered_rows])
        unemployment_ma = AnalyticsService._moving_average([row["unemployment_rate"] for row in ordered_rows])
        natural_increase_ma = AnalyticsService._moving_average([row["natural_increase"] for row in ordered_rows])
        average_salary_ma = AnalyticsService._moving_average([row["average_salary"] for row in ordered_rows])
        vrp_ma = AnalyticsService._moving_average([row["vrp"] for row in ordered_rows])
        migration_balance_ma = AnalyticsService._moving_average([row["migration_balance"] for row in ordered_rows])

        metrics: list[dict] = []
        previous_row: dict | None = None

        for index, row in enumerate(ordered_rows):
            population_growth_rate = None
            salary_growth_rate = None
            vrp_growth_rate = None
            unemployment_delta = None
            natural_increase_delta = None
            adjusted_population_change = AnalyticsService._safe_divide(
                row["natural_increase"],
                row["population"],
            )
            migration_rate = row["migration_balance"]
            natural_increase_rate = AnalyticsService._safe_divide(
                row["natural_increase"] * 10000 if row["natural_increase"] is not None else None,
                row["population"],
            )
            vrp_per_capita = AnalyticsService._safe_divide(
                row["vrp"],
                row["population"],
            )
            salary_to_vrp_ratio = AnalyticsService._safe_divide(
                row["average_salary"],
                vrp_per_capita,
            )
            natural_increase_share = None
            migration_estimate = None
            total_demographic_balance = None
            demographic_balance_rate = None

            if previous_row and row["year"] == previous_row["year"] + 1:
                population_growth_rate = AnalyticsService._calculate_growth(
                    row["population"],
                    previous_row["population"],
                )
                salary_growth_rate = AnalyticsService._calculate_growth(
                    row["average_salary"],
                    previous_row["average_salary"],
                )
                vrp_growth_rate = AnalyticsService._calculate_growth(
                    row["vrp"],
                    previous_row["vrp"],
                )
                unemployment_delta = AnalyticsService._calculate_delta(
                    row["unemployment_rate"],
                    previous_row["unemployment_rate"],
                )
                natural_increase_delta = AnalyticsService._calculate_delta(
                    row["natural_increase"],
                    previous_row["natural_increase"],
                )

                population_delta = AnalyticsService._calculate_delta(
                    row["population"],
                    previous_row["population"],
                )
                natural_increase_share = AnalyticsService._safe_divide(
                    row["natural_increase"],
                    population_delta,
                )
                migration_estimate = AnalyticsService._safe_divide(
                    row["migration_balance"] * row["population"] if row["migration_balance"] is not None and row["population"] is not None else None,
                    10000,
                )
                if row["natural_increase"] is not None and migration_estimate is not None:
                    total_demographic_balance = row["natural_increase"] + migration_estimate
                if natural_increase_rate is not None and migration_rate is not None:
                    demographic_balance_rate = natural_increase_rate + migration_rate

            metrics.append(
                {
                    "year": row["year"],
                    "population_growth_rate": population_growth_rate,
                    "salary_growth_rate": salary_growth_rate,
                    "vrp_growth_rate": vrp_growth_rate,
                    "unemployment_delta": unemployment_delta,
                    "natural_increase_delta": natural_increase_delta,
                    "adjusted_population_change": adjusted_population_change,
                    "natural_increase_share": natural_increase_share,
                    "migration_estimate": migration_estimate,
                    "migration_rate": migration_rate,
                    "natural_increase_rate": natural_increase_rate,
                    "total_demographic_balance": total_demographic_balance,
                    "demographic_balance_rate": demographic_balance_rate,
                    "vrp_per_capita": vrp_per_capita,
                    "salary_to_vrp_ratio": salary_to_vrp_ratio,
                    "population_moving_average": population_ma[index],
                    "unemployment_moving_average": unemployment_ma[index],
                    "natural_increase_moving_average": natural_increase_ma[index],
                    "average_salary_moving_average": average_salary_ma[index],
                    "vrp_moving_average": vrp_ma[index],
                    "migration_balance_moving_average": migration_balance_ma[index],
                }
            )
            previous_row = row

        return metrics

    @staticmethod
    def _group_rows_by_region(rows: list[dict]) -> dict[int, list[dict]]:
        grouped: dict[int, list[dict]] = defaultdict(list)
        for row in rows:
            grouped[row["region_id"]].append(row)
        return grouped

    @staticmethod
    def _build_year_cross_section(rows: list[dict], year: int) -> list[dict]:
        rows_by_region = AnalyticsService._group_rows_by_region(rows)
        cross_section: list[dict] = []

        for region_rows in rows_by_region.values():
            dataset_row = next((item for item in region_rows if item["year"] == year), None)
            if not dataset_row:
                continue
            metrics_row = next(
                (item for item in AnalyticsService._build_region_metrics(region_rows) if item["year"] == year),
                None,
            )
            cross_section.append(
                {
                    **dataset_row,
                    **(metrics_row or {}),
                }
            )

        return sorted(cross_section, key=lambda item: item["region_name"])

    @staticmethod
    async def get_region_growth_metrics(
        session: AsyncSession,
        region_id: int,
    ) -> list[dict]:
        rows = await AnalyticsService.get_analytics_dataset(session=session, region_id=region_id)
        return AnalyticsService._build_region_metrics(rows)

    @staticmethod
    async def get_region_trends(
        session: AsyncSession,
        region_id: int,
    ) -> list[dict]:
        rows = await AnalyticsService.get_analytics_dataset(session=session, region_id=region_id)
        metrics = await AnalyticsService.get_region_growth_metrics(session=session, region_id=region_id)

        return [
            {"metric": "population", **AnalyticsService._linear_regression({row["year"]: row["population"] for row in rows})},
            {"metric": "unemployment_rate", **AnalyticsService._linear_regression({row["year"]: row["unemployment_rate"] for row in rows})},
            {"metric": "natural_increase", **AnalyticsService._linear_regression({row["year"]: row["natural_increase"] for row in rows})},
            {"metric": "average_salary", **AnalyticsService._linear_regression({row["year"]: row["average_salary"] for row in rows})},
            {"metric": "vrp", **AnalyticsService._linear_regression({row["year"]: row["vrp"] for row in rows})},
            {"metric": "migration_balance", **AnalyticsService._linear_regression({row["year"]: row["migration_balance"] for row in rows})},
            {"metric": "salary_growth_rate", **AnalyticsService._linear_regression({row["year"]: row["salary_growth_rate"] for row in metrics})},
            {"metric": "vrp_growth_rate", **AnalyticsService._linear_regression({row["year"]: row["vrp_growth_rate"] for row in metrics})},
        ]

    @staticmethod
    async def get_top_regions_by_low_unemployment(
        session: AsyncSession,
        year: int,
        limit: int = 10,
    ) -> list[dict]:
        rows = await AnalyticsService.get_analytics_dataset(session=session, start_year=year, end_year=year)
        cross_section = AnalyticsService._build_year_cross_section(rows, year)
        ranked = [row for row in cross_section if row["unemployment_rate"] is not None]
        ranked.sort(key=lambda row: (row["unemployment_rate"], row["region_name"]))
        return ranked[:limit]

    @staticmethod
    async def get_top_regions_by_population_growth(
        session: AsyncSession,
        year: int,
        limit: int = 10,
    ) -> list[dict]:
        rows = await AnalyticsService.get_analytics_dataset(session=session, start_year=year - 1, end_year=year)
        cross_section = AnalyticsService._build_year_cross_section(rows, year)
        ranked = [row for row in cross_section if row["population_growth_rate"] is not None]
        ranked.sort(key=lambda row: (-row["population_growth_rate"], row["region_name"]))
        return [
            {
                "region_id": row["region_id"],
                "region_name": row["region_name"],
                "year": row["year"],
                "population_growth_rate": row["population_growth_rate"],
            }
            for row in ranked[:limit]
        ]

    @staticmethod
    async def get_regions_with_largest_unemployment_decline(
        session: AsyncSession,
        year: int,
        limit: int = 10,
    ) -> list[dict]:
        rows = await AnalyticsService.get_analytics_dataset(session=session, start_year=year - 1, end_year=year)
        cross_section = AnalyticsService._build_year_cross_section(rows, year)
        ranked = [row for row in cross_section if row["unemployment_delta"] is not None]
        ranked.sort(key=lambda row: (row["unemployment_delta"], row["region_name"]))
        return [
            {
                "region_id": row["region_id"],
                "region_name": row["region_name"],
                "year": row["year"],
                "unemployment_delta": row["unemployment_delta"],
            }
            for row in ranked[:limit]
        ]

    @staticmethod
    async def get_top_regions_by_natural_increase(
        session: AsyncSession,
        year: int,
        limit: int = 10,
    ) -> list[dict]:
        rows = await AnalyticsService.get_analytics_dataset(session=session, start_year=year, end_year=year)
        cross_section = AnalyticsService._build_year_cross_section(rows, year)
        ranked = [row for row in cross_section if row["natural_increase"] is not None]
        ranked.sort(key=lambda row: (-row["natural_increase"], row["region_name"]))
        return [
            {
                "region_id": row["region_id"],
                "region_name": row["region_name"],
                "year": row["year"],
                "natural_increase": row["natural_increase"],
            }
            for row in ranked[:limit]
        ]

    @staticmethod
    async def get_regions_with_largest_natural_decrease(
        session: AsyncSession,
        year: int,
        limit: int = 10,
    ) -> list[dict]:
        rows = await AnalyticsService.get_analytics_dataset(session=session, start_year=year, end_year=year)
        cross_section = AnalyticsService._build_year_cross_section(rows, year)
        ranked = [row for row in cross_section if row["natural_increase"] is not None]
        ranked.sort(key=lambda row: (row["natural_increase"], row["region_name"]))
        return [
            {
                "region_id": row["region_id"],
                "region_name": row["region_name"],
                "year": row["year"],
                "natural_increase": row["natural_increase"],
            }
            for row in ranked[:limit]
        ]

    @staticmethod
    async def get_regions_with_best_natural_increase_improvement(
        session: AsyncSession,
        year: int,
        limit: int = 10,
    ) -> list[dict]:
        rows = await AnalyticsService.get_analytics_dataset(session=session, start_year=year - 1, end_year=year)
        cross_section = AnalyticsService._build_year_cross_section(rows, year)
        ranked = [row for row in cross_section if row["natural_increase_delta"] is not None]
        ranked.sort(key=lambda row: (-row["natural_increase_delta"], row["region_name"]))
        return [
            {
                "region_id": row["region_id"],
                "region_name": row["region_name"],
                "year": row["year"],
                "natural_increase_delta": row["natural_increase_delta"],
            }
            for row in ranked[:limit]
        ]

    @staticmethod
    async def get_top_regions_by_salary(
        session: AsyncSession,
        year: int,
        limit: int = 10,
    ) -> list[dict]:
        rows = await AnalyticsService.get_analytics_dataset(session=session, start_year=year, end_year=year)
        cross_section = AnalyticsService._build_year_cross_section(rows, year)
        ranked = [row for row in cross_section if row["average_salary"] is not None]
        ranked.sort(key=lambda row: (-row["average_salary"], row["region_name"]))
        return [
            {
                "region_id": row["region_id"],
                "region_name": row["region_name"],
                "year": row["year"],
                "average_salary": row["average_salary"],
            }
            for row in ranked[:limit]
        ]

    @staticmethod
    async def get_top_regions_by_salary_growth(
        session: AsyncSession,
        year: int,
        limit: int = 10,
    ) -> list[dict]:
        rows = await AnalyticsService.get_analytics_dataset(session=session, start_year=year - 1, end_year=year)
        cross_section = AnalyticsService._build_year_cross_section(rows, year)
        ranked = [row for row in cross_section if row["salary_growth_rate"] is not None]
        ranked.sort(key=lambda row: (-row["salary_growth_rate"], row["region_name"]))
        return [
            {
                "region_id": row["region_id"],
                "region_name": row["region_name"],
                "year": row["year"],
                "salary_growth_rate": row["salary_growth_rate"],
            }
            for row in ranked[:limit]
        ]

    @staticmethod
    async def get_top_regions_by_vrp_per_capita(
        session: AsyncSession,
        year: int,
        limit: int = 10,
    ) -> list[dict]:
        rows = await AnalyticsService.get_analytics_dataset(session=session, start_year=year, end_year=year)
        cross_section = AnalyticsService._build_year_cross_section(rows, year)
        ranked = [row for row in cross_section if row["vrp_per_capita"] is not None]
        ranked.sort(key=lambda row: (-row["vrp_per_capita"], row["region_name"]))
        return [
            {
                "region_id": row["region_id"],
                "region_name": row["region_name"],
                "year": row["year"],
                "vrp_per_capita": row["vrp_per_capita"],
            }
            for row in ranked[:limit]
        ]

    @staticmethod
    async def get_top_regions_by_migration_attractiveness(
        session: AsyncSession,
        year: int,
        limit: int = 10,
    ) -> list[dict]:
        rows = await AnalyticsService.get_analytics_dataset(session=session, start_year=year, end_year=year)
        cross_section = AnalyticsService._build_year_cross_section(rows, year)
        ranked = [row for row in cross_section if row["migration_rate"] is not None]
        ranked.sort(key=lambda row: (-row["migration_rate"], row["region_name"]))
        return [
            {
                "region_id": row["region_id"],
                "region_name": row["region_name"],
                "year": row["year"],
                "migration_rate": row["migration_rate"],
            }
            for row in ranked[:limit]
        ]

    @staticmethod
    async def get_top_regions_by_demographic_balance(
        session: AsyncSession,
        year: int,
        limit: int = 10,
    ) -> list[dict]:
        rows = await AnalyticsService.get_analytics_dataset(session=session, start_year=year - 1, end_year=year)
        cross_section = AnalyticsService._build_year_cross_section(rows, year)
        ranked = [row for row in cross_section if row["demographic_balance_rate"] is not None]
        ranked.sort(key=lambda row: (-row["demographic_balance_rate"], row["region_name"]))
        return [
            {
                "region_id": row["region_id"],
                "region_name": row["region_name"],
                "year": row["year"],
                "demographic_balance_rate": row["demographic_balance_rate"],
            }
            for row in ranked[:limit]
        ]

    @staticmethod
    async def get_normalized_economic_metrics(
        session: AsyncSession,
        year: int,
    ) -> list[dict]:
        rows = await AnalyticsService.get_analytics_dataset(session=session, start_year=year - 1, end_year=year)
        cross_section = AnalyticsService._build_year_cross_section(rows, year)

        salary_growth_values = [row["salary_growth_rate"] for row in cross_section if row["salary_growth_rate"] is not None]
        vrp_per_capita_values = [row["vrp_per_capita"] for row in cross_section if row["vrp_per_capita"] is not None]
        unemployment_values = [row["unemployment_rate"] for row in cross_section if row["unemployment_rate"] is not None]

        items: list[dict] = []
        for row in cross_section:
            items.append(
                {
                    "region_id": row["region_id"],
                    "region_name": row["region_name"],
                    "year": row["year"],
                    "salary_growth_rate": row["salary_growth_rate"],
                    "vrp_per_capita": row["vrp_per_capita"],
                    "unemployment_rate": row["unemployment_rate"],
                    "z_salary_growth_rate": AnalyticsService._z_score(row["salary_growth_rate"], salary_growth_values),
                    "z_vrp_per_capita": AnalyticsService._z_score(row["vrp_per_capita"], vrp_per_capita_values),
                    "z_unemployment_rate": AnalyticsService._z_score(row["unemployment_rate"], unemployment_values),
                    "minmax_salary_growth_rate": AnalyticsService._minmax(row["salary_growth_rate"], salary_growth_values),
                    "minmax_vrp_per_capita": AnalyticsService._minmax(row["vrp_per_capita"], vrp_per_capita_values),
                    "minmax_unemployment_rate": AnalyticsService._minmax(row["unemployment_rate"], unemployment_values),
                }
            )
        return items

    @staticmethod
    async def get_normalized_demographic_metrics(
        session: AsyncSession,
        year: int,
    ) -> list[dict]:
        rows = await AnalyticsService.get_analytics_dataset(session=session, start_year=year - 1, end_year=year)
        cross_section = AnalyticsService._build_year_cross_section(rows, year)

        population_growth_values = [row["population_growth_rate"] for row in cross_section if row["population_growth_rate"] is not None]
        natural_increase_rate_values = [row["natural_increase_rate"] for row in cross_section if row["natural_increase_rate"] is not None]
        migration_rate_values = [row["migration_rate"] for row in cross_section if row["migration_rate"] is not None]

        items: list[dict] = []
        for row in cross_section:
            items.append(
                {
                    "region_id": row["region_id"],
                    "region_name": row["region_name"],
                    "year": row["year"],
                    "population_growth_rate": row["population_growth_rate"],
                    "natural_increase_rate": row["natural_increase_rate"],
                    "migration_rate": row["migration_rate"],
                    "z_population_growth_rate": AnalyticsService._z_score(row["population_growth_rate"], population_growth_values),
                    "z_natural_increase_rate": AnalyticsService._z_score(row["natural_increase_rate"], natural_increase_rate_values),
                    "z_migration_rate": AnalyticsService._z_score(row["migration_rate"], migration_rate_values),
                    "minmax_population_growth_rate": AnalyticsService._minmax(row["population_growth_rate"], population_growth_values),
                    "minmax_natural_increase_rate": AnalyticsService._minmax(row["natural_increase_rate"], natural_increase_rate_values),
                    "minmax_migration_rate": AnalyticsService._minmax(row["migration_rate"], migration_rate_values),
                }
            )
        return items

    @staticmethod
    async def get_composite_economic_index(
        session: AsyncSession,
        year: int,
        limit: int = 10,
        w1: float = 0.35,
        w2: float = 0.35,
        w3: float = 0.30,
    ) -> list[dict]:
        items = await AnalyticsService.get_normalized_economic_metrics(session=session, year=year)
        ranked: list[dict] = []
        for item in items:
            score = (
                w1 * (item["z_salary_growth_rate"] or 0.0)
                + w2 * (item["z_vrp_per_capita"] or 0.0)
                - w3 * (item["z_unemployment_rate"] or 0.0)
            )
            ranked.append(
                {
                    "region_id": item["region_id"],
                    "region_name": item["region_name"],
                    "year": item["year"],
                    "composite_economic_index": score,
                    "salary_growth_rate": item["salary_growth_rate"],
                    "vrp_per_capita": item["vrp_per_capita"],
                    "unemployment_rate": item["unemployment_rate"],
                }
            )
        ranked.sort(key=lambda row: (-row["composite_economic_index"], row["region_name"]))
        return ranked[:limit]

    @staticmethod
    async def get_composite_demographic_index(
        session: AsyncSession,
        year: int,
        limit: int = 10,
        w1: float = 0.34,
        w2: float = 0.33,
        w3: float = 0.33,
    ) -> list[dict]:
        items = await AnalyticsService.get_normalized_demographic_metrics(session=session, year=year)
        ranked: list[dict] = []
        for item in items:
            score = (
                w1 * (item["z_population_growth_rate"] or 0.0)
                + w2 * (item["z_natural_increase_rate"] or 0.0)
                + w3 * (item["z_migration_rate"] or 0.0)
            )
            ranked.append(
                {
                    "region_id": item["region_id"],
                    "region_name": item["region_name"],
                    "year": item["year"],
                    "composite_demographic_index": score,
                    "population_growth_rate": item["population_growth_rate"],
                    "natural_increase_rate": item["natural_increase_rate"],
                    "migration_rate": item["migration_rate"],
                }
            )
        ranked.sort(key=lambda row: (-row["composite_demographic_index"], row["region_name"]))
        return ranked[:limit]

    @staticmethod
    async def get_population_unemployment_correlation(
        session: AsyncSession,
        region_id: int,
    ) -> float | None:
        rows = await AnalyticsService.get_analytics_dataset(session=session, region_id=region_id)
        pairs = [
            (row["population"], row["unemployment_rate"])
            for row in rows
            if row["population"] is not None and row["unemployment_rate"] is not None
        ]
        return AnalyticsService._pearson_correlation(
            [x for x, _ in pairs],
            [y for _, y in pairs],
        )

    @staticmethod
    async def get_region_correlations(
        session: AsyncSession,
        region_id: int,
    ) -> dict:
        rows = await AnalyticsService.get_analytics_dataset(session=session, region_id=region_id)
        metrics = AnalyticsService._build_region_metrics(rows)

        pop_unemployment_pairs = [
            (row["population"], row["unemployment_rate"])
            for row in rows
            if row["population"] is not None and row["unemployment_rate"] is not None
        ]
        natural_pop_growth_pairs = [
            (row["natural_increase"], metric["population_growth_rate"])
            for row, metric in zip(sorted(rows, key=lambda item: item["year"]), metrics)
            if row["natural_increase"] is not None and metric["population_growth_rate"] is not None
        ]
        natural_unemployment_pairs = [
            (row["natural_increase"], row["unemployment_rate"])
            for row in rows
            if row["natural_increase"] is not None and row["unemployment_rate"] is not None
        ]

        return {
            "region_id": region_id,
            "population_unemployment_correlation": AnalyticsService._pearson_correlation(
                [x for x, _ in pop_unemployment_pairs],
                [y for _, y in pop_unemployment_pairs],
            ),
            "natural_increase_population_growth_correlation": AnalyticsService._pearson_correlation(
                [x for x, _ in natural_pop_growth_pairs],
                [y for _, y in natural_pop_growth_pairs],
            ),
            "natural_increase_unemployment_correlation": AnalyticsService._pearson_correlation(
                [x for x, _ in natural_unemployment_pairs],
                [y for _, y in natural_unemployment_pairs],
            ),
        }
