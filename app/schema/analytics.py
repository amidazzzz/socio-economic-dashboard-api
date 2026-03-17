from pydantic import BaseModel


class RegionYearAnalytics(BaseModel):
    year: int
    population: float | None
    unemployment_rate: float | None
