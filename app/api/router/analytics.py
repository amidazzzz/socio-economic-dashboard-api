from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schema.analytics import (
    AnalyticsDatasetItem,
    CorrelationResponse,
    DemographicBalanceRankingItem,
    DemographicCompositeIndexItem,
    DemographicNormalizedItem,
    EconomicCompositeIndexItem,
    EconomicNormalizedItem,
    MigrationAttractivenessRankingItem,
    MultiCorrelationResponse,
    NaturalIncreaseDeltaRankingItem,
    NaturalIncreaseRankingItem,
    PopulationGrowthRankingItem,
    RegionAnalyticsMetrics,
    RegionTrendItem,
    RegionYearAnalytics,
    SalaryGrowthRankingItem,
    SalaryRankingItem,
    UnemploymentDeclineRankingItem,
    UnemploymentRankingItem,
    VrpPerCapitaRankingItem,
)
from app.service.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dataset", response_model=list[AnalyticsDatasetItem])
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


@router.get("/region/{region_id}", response_model=list[RegionYearAnalytics])
async def get_region_analytics(
    region_id: int,
    session: AsyncSession = Depends(get_db),
):
    return await AnalyticsService.get_region_year_analytics(
        session=session,
        region_id=region_id,
    )


@router.get("/region/{region_id}/correlation", response_model=CorrelationResponse)
async def get_region_correlation(
    region_id: int,
    session: AsyncSession = Depends(get_db),
):
    value = await AnalyticsService.get_population_unemployment_correlation(
        session=session,
        region_id=region_id,
    )
    return {"region_id": region_id, "correlation": value}


@router.get("/region/{region_id}/correlations", response_model=MultiCorrelationResponse)
async def get_region_correlations(
    region_id: int,
    session: AsyncSession = Depends(get_db),
):
    return await AnalyticsService.get_region_correlations(
        session=session,
        region_id=region_id,
    )


@router.get("/region/{region_id}/metrics", response_model=list[RegionAnalyticsMetrics])
@router.get("/region/{region_id}/growth", response_model=list[RegionAnalyticsMetrics])
async def get_region_metrics(
    region_id: int,
    session: AsyncSession = Depends(get_db),
):
    return await AnalyticsService.get_region_growth_metrics(
        session=session,
        region_id=region_id,
    )


@router.get("/region/{region_id}/trends", response_model=list[RegionTrendItem])
async def get_region_trends(
    region_id: int,
    session: AsyncSession = Depends(get_db),
):
    return await AnalyticsService.get_region_trends(
        session=session,
        region_id=region_id,
    )


@router.get("/normalized/economic", response_model=list[EconomicNormalizedItem])
async def get_normalized_economic_metrics(
    year: int,
    session: AsyncSession = Depends(get_db),
):
    return await AnalyticsService.get_normalized_economic_metrics(
        session=session,
        year=year,
    )


@router.get("/normalized/demographic", response_model=list[DemographicNormalizedItem])
async def get_normalized_demographic_metrics(
    year: int,
    session: AsyncSession = Depends(get_db),
):
    return await AnalyticsService.get_normalized_demographic_metrics(
        session=session,
        year=year,
    )


@router.get("/composite-index/economic", response_model=list[EconomicCompositeIndexItem])
async def get_composite_economic_index(
    year: int,
    limit: int = 10,
    w1: float = 0.35,
    w2: float = 0.35,
    w3: float = 0.30,
    session: AsyncSession = Depends(get_db),
):
    return await AnalyticsService.get_composite_economic_index(
        session=session,
        year=year,
        limit=limit,
        w1=w1,
        w2=w2,
        w3=w3,
    )


@router.get("/composite-index/demographic", response_model=list[DemographicCompositeIndexItem])
async def get_composite_demographic_index(
    year: int,
    limit: int = 10,
    w1: float = 0.34,
    w2: float = 0.33,
    w3: float = 0.33,
    session: AsyncSession = Depends(get_db),
):
    return await AnalyticsService.get_composite_demographic_index(
        session=session,
        year=year,
        limit=limit,
        w1=w1,
        w2=w2,
        w3=w3,
    )


@router.get("/rankings/lowest-unemployment", response_model=list[UnemploymentRankingItem])
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


@router.get("/rankings/population-growth", response_model=list[PopulationGrowthRankingItem])
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


@router.get("/rankings/unemployment-decline", response_model=list[UnemploymentDeclineRankingItem])
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


@router.get("/rankings/natural-increase", response_model=list[NaturalIncreaseRankingItem])
async def get_natural_increase_ranking(
    year: int,
    limit: int = 10,
    session: AsyncSession = Depends(get_db),
):
    return await AnalyticsService.get_top_regions_by_natural_increase(
        session=session,
        year=year,
        limit=limit,
    )


@router.get("/rankings/natural-decrease", response_model=list[NaturalIncreaseRankingItem])
async def get_natural_decrease_ranking(
    year: int,
    limit: int = 10,
    session: AsyncSession = Depends(get_db),
):
    return await AnalyticsService.get_regions_with_largest_natural_decrease(
        session=session,
        year=year,
        limit=limit,
    )


@router.get("/rankings/natural-increase-improvement", response_model=list[NaturalIncreaseDeltaRankingItem])
async def get_natural_increase_improvement_ranking(
    year: int,
    limit: int = 10,
    session: AsyncSession = Depends(get_db),
):
    return await AnalyticsService.get_regions_with_best_natural_increase_improvement(
        session=session,
        year=year,
        limit=limit,
    )


@router.get("/rankings/salary", response_model=list[SalaryRankingItem])
async def get_salary_ranking(
    year: int,
    limit: int = 10,
    session: AsyncSession = Depends(get_db),
):
    return await AnalyticsService.get_top_regions_by_salary(
        session=session,
        year=year,
        limit=limit,
    )


@router.get("/rankings/salary-growth", response_model=list[SalaryGrowthRankingItem])
async def get_salary_growth_ranking(
    year: int,
    limit: int = 10,
    session: AsyncSession = Depends(get_db),
):
    return await AnalyticsService.get_top_regions_by_salary_growth(
        session=session,
        year=year,
        limit=limit,
    )


@router.get("/rankings/vrp-per-capita", response_model=list[VrpPerCapitaRankingItem])
async def get_vrp_per_capita_ranking(
    year: int,
    limit: int = 10,
    session: AsyncSession = Depends(get_db),
):
    return await AnalyticsService.get_top_regions_by_vrp_per_capita(
        session=session,
        year=year,
        limit=limit,
    )


@router.get("/rankings/migration-attractiveness", response_model=list[MigrationAttractivenessRankingItem])
async def get_migration_attractiveness_ranking(
    year: int,
    limit: int = 10,
    session: AsyncSession = Depends(get_db),
):
    return await AnalyticsService.get_top_regions_by_migration_attractiveness(
        session=session,
        year=year,
        limit=limit,
    )


@router.get("/rankings/demographic-balance", response_model=list[DemographicBalanceRankingItem])
async def get_demographic_balance_ranking(
    year: int,
    limit: int = 10,
    session: AsyncSession = Depends(get_db),
):
    return await AnalyticsService.get_top_regions_by_demographic_balance(
        session=session,
        year=year,
        limit=limit,
    )


@router.get("/top-unemployment", response_model=list[UnemploymentRankingItem])
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
