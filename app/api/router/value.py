from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.model.indicator_value import IndicatorValue
from app.schema.value import TimeSeriesResponse, TimeSeriesItem


router = APIRouter(tags=["values"])


@router.get("/values", response_model=TimeSeriesResponse)
async def get_values(
    indicator_id: int = Query(...),
    region_id: int = Query(...),
    start_year: int | None = None,
    end_year: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(IndicatorValue).where(
        IndicatorValue.indicator_id == indicator_id,
        IndicatorValue.region_id == region_id,
    )

    if start_year:
        stmt = stmt.where(IndicatorValue.year >= start_year)
    if end_year:
        stmt = stmt.where(IndicatorValue.year <= end_year)

    stmt = stmt.order_by(IndicatorValue.year)

    result = await db.execute(stmt)
    rows = result.scalars().all()

    return TimeSeriesResponse(
        indicator_id=indicator_id,
        region_id=region_id,
        series=[
            TimeSeriesItem(year=row.year, value=float(row.value))
            for row in rows
        ],
    )
