from dataclasses import dataclass
from typing import TypedDict


class IndicatorValueRecord(TypedDict):
    region_name: str
    year: int
    period: str
    value: float | int
    source: str


@dataclass(slots=True)
class ETLJobResult:
    job_name: str
    extracted_rows: int | None = None
    transformed_rows: int | None = None
    loaded_rows: int | None = None
