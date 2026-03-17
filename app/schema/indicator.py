from pydantic import BaseModel
from app.schema.unit import UnitResponse


class IndicatorResponse(BaseModel):
    id: int
    code: str
    name: str
    description: str | None
    unit: UnitResponse

    class Config:
        from_attributes = True
