from pydantic import BaseModel


class RegionBase(BaseModel):
    id: int
    code: str
    name: str
    type: str
    parent_id: int | None


class RegionResponse(RegionBase):
    class Config:
        from_attributes = True
