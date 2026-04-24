from pydantic import BaseModel


class RegionYearAnalytics(BaseModel):
    year: int
    population: float | None
    unemployment_rate: float | None
    natural_increase: float | None
    migration_balance: float | None
    average_salary: float | None
    vrp: float | None


class AnalyticsDatasetItem(RegionYearAnalytics):
    region_id: int
    region_name: str


class RegionAnalyticsMetrics(BaseModel):
    year: int
    population_growth_rate: float | None
    salary_growth_rate: float | None
    vrp_growth_rate: float | None
    unemployment_delta: float | None
    natural_increase_delta: float | None
    adjusted_population_change: float | None
    natural_increase_share: float | None
    migration_estimate: float | None
    migration_rate: float | None
    natural_increase_rate: float | None
    total_demographic_balance: float | None
    demographic_balance_rate: float | None
    vrp_per_capita: float | None
    salary_to_vrp_ratio: float | None
    population_moving_average: float | None
    unemployment_moving_average: float | None
    natural_increase_moving_average: float | None
    average_salary_moving_average: float | None
    vrp_moving_average: float | None
    migration_balance_moving_average: float | None


class CorrelationResponse(BaseModel):
    region_id: int
    correlation: float | None


class MultiCorrelationResponse(BaseModel):
    region_id: int
    population_unemployment_correlation: float | None
    natural_increase_population_growth_correlation: float | None
    natural_increase_unemployment_correlation: float | None


class RegionTrendItem(BaseModel):
    metric: str
    slope: float | None
    intercept: float | None


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


class NaturalIncreaseRankingItem(BaseModel):
    region_id: int
    region_name: str
    year: int
    natural_increase: float


class NaturalIncreaseDeltaRankingItem(BaseModel):
    region_id: int
    region_name: str
    year: int
    natural_increase_delta: float


class SalaryRankingItem(BaseModel):
    region_id: int
    region_name: str
    year: int
    average_salary: float


class SalaryGrowthRankingItem(BaseModel):
    region_id: int
    region_name: str
    year: int
    salary_growth_rate: float


class VrpPerCapitaRankingItem(BaseModel):
    region_id: int
    region_name: str
    year: int
    vrp_per_capita: float


class MigrationAttractivenessRankingItem(BaseModel):
    region_id: int
    region_name: str
    year: int
    migration_rate: float


class DemographicBalanceRankingItem(BaseModel):
    region_id: int
    region_name: str
    year: int
    demographic_balance_rate: float


class EconomicNormalizedItem(BaseModel):
    region_id: int
    region_name: str
    year: int
    salary_growth_rate: float | None
    vrp_per_capita: float | None
    unemployment_rate: float | None
    z_salary_growth_rate: float | None
    z_vrp_per_capita: float | None
    z_unemployment_rate: float | None
    minmax_salary_growth_rate: float | None
    minmax_vrp_per_capita: float | None
    minmax_unemployment_rate: float | None


class DemographicNormalizedItem(BaseModel):
    region_id: int
    region_name: str
    year: int
    population_growth_rate: float | None
    natural_increase_rate: float | None
    migration_rate: float | None
    z_population_growth_rate: float | None
    z_natural_increase_rate: float | None
    z_migration_rate: float | None
    minmax_population_growth_rate: float | None
    minmax_natural_increase_rate: float | None
    minmax_migration_rate: float | None


class EconomicCompositeIndexItem(BaseModel):
    region_id: int
    region_name: str
    year: int
    composite_economic_index: float
    salary_growth_rate: float | None
    vrp_per_capita: float | None
    unemployment_rate: float | None


class DemographicCompositeIndexItem(BaseModel):
    region_id: int
    region_name: str
    year: int
    composite_demographic_index: float
    population_growth_rate: float | None
    natural_increase_rate: float | None
    migration_rate: float | None
