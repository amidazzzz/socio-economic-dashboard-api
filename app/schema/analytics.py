from pydantic import BaseModel


class RegionYearAnalytics(BaseModel):
    year: int
    population: float
    unemployment_rate: float


class AnalyticsDatasetItem(BaseModel):
    region_id: int
    region_name: str
    year: int
    population: float
    unemployment_rate: float


class RegionAnalyticsMetrics(BaseModel):
    year: int
    population_growth_rate: float | None
    unemployment_delta: float | None


class UnemploymentRankingItem(BaseModel):
    region_id: int
    region_name: str
    year: int
    unemployment_rate: float


class PopulationGrowthRankingItem(BaseModel):
    region_id: int
    region_name: str
    year: int
    population_growth_rate: float


class UnemploymentDeclineRankingItem(BaseModel):
    region_id: int
    region_name: str
    year: int
    unemployment_delta: float
