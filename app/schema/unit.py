from pydantic import BaseModel


class UnitResponse(BaseModel):
    id: int
    code: str
    name: str

    class Config:
        from_attributes = True
