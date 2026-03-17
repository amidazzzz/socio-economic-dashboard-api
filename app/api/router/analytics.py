from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schema.analytics import (
    AnalyticsDatasetItem,
    PopulationGrowthRankingItem,
    RegionAnalyticsMetrics,
    RegionYearAnalytics,
    UnemploymentDeclineRankingItem,
    UnemploymentRankingItem,
)
from app.service.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/dataset",
    response_model=list[AnalyticsDatasetItem],
)
async def get_analytics_dataset(
    region_id: int | None = None,
    start_year: int | None = None,
    end_year: int | None = None,
    session: AsyncSession = Depends(get_db),
):
    return await AnalyticsService.get_analytics_dataset(
        session=session,
        region_id=region_id,
        start_year=start_year,
        end_year=end_year,
    )


@router.get(
    "/region/{region_id}",
    response_model=list[RegionYearAnalytics],
)
async def get_region_analytics(
    region_id: int,
    session: AsyncSession = Depends(get_db),
):
    return await AnalyticsService.get_region_year_analytics(
        session=session,
        region_id=region_id,
    )

@router.get("/region/{region_id}/correlation")
async def get_region_correlation(
    region_id: int,
    session: AsyncSession = Depends(get_db),
):
    value = await AnalyticsService.get_population_unemployment_correlation(
        session=session,
        region_id=region_id,
    )

    return {
        "region_id": region_id,
        "correlation": value,
    }

@router.get(
    "/rankings/lowest-unemployment",
    response_model=list[UnemploymentRankingItem],
)
async def get_lowest_unemployment_regions(
    year: int,
    limit: int = 10,
    session: AsyncSession = Depends(get_db),
):
    return await AnalyticsService.get_top_regions_by_low_unemployment(
        session=session,
        year=year,
        limit=limit,
    )

@router.get(
    "/rankings/population-growth",
    response_model=list[PopulationGrowthRankingItem],
)
async def get_population_growth_ranking(
    year: int,
    limit: int = 10,
    session: AsyncSession = Depends(get_db),
):
    return await AnalyticsService.get_top_regions_by_population_growth(
        session=session,
        year=year,
        limit=limit,
    )


@router.get(
    "/rankings/unemployment-decline",
    response_model=list[UnemploymentDeclineRankingItem],
)
async def get_unemployment_decline_ranking(
    year: int,
    limit: int = 10,
    session: AsyncSession = Depends(get_db),
):
    return await AnalyticsService.get_regions_with_largest_unemployment_decline(
        session=session,
        year=year,
        limit=limit,
    )


@router.get(
    "/region/{region_id}/metrics",
    response_model=list[RegionAnalyticsMetrics],
)
@router.get(
    "/region/{region_id}/growth",
    response_model=list[RegionAnalyticsMetrics],
)
async def get_region_metrics(
    region_id: int,
    session: AsyncSession = Depends(get_db),
):
    return await AnalyticsService.get_region_growth_metrics(
        session=session,
        region_id=region_id,
    )


@router.get(
    "/top-unemployment",
    response_model=list[UnemploymentRankingItem],
)
async def get_top_unemployment_regions(
    year: int,
    limit: int = 10,
    session: AsyncSession = Depends(get_db),
):
    return await AnalyticsService.get_top_regions_by_low_unemployment(
        session=session,
        year=year,
        limit=limit,
    )
