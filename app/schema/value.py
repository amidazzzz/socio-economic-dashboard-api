from pydantic import BaseModel


class TimeSeriesItem(BaseModel):
    year: int
    value: float


class TimeSeriesResponse(BaseModel):
    indicator_id: int
    region_id: int
    series: list[TimeSeriesItem]
