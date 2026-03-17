from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schema.analytics import RegionYearAnalytics
from app.service.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


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

@router.get("/top-unemployment")
async def get_top_unemployment_regions(
    year: int,
    limit: int = 10,
    session: AsyncSession = Depends(get_db),
):
    return await AnalyticsService.get_top_regions_by_unemployment(
        session=session,
        year=year,
        limit=limit,
    )

@router.get("/region/{region_id}/growth")
async def get_region_growth(
    region_id: int,
    session: AsyncSession = Depends(get_db),
):
    return await AnalyticsService.get_region_growth_rates(
        session=session,
        region_id=region_id,
    )