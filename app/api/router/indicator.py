from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.model.indicator import Indicator
from app.schema.indicator import IndicatorResponse


router = APIRouter(tags=["indicators"])


@router.get("/indicators", response_model=list[IndicatorResponse])
async def get_indicators(db: AsyncSession = Depends(get_db)):
    stmt = select(Indicator).options(selectinload(Indicator.unit))
    result = await db.execute(stmt)
    return result.scalars().all()
