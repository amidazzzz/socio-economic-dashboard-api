from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.model.region import Region
from app.service.analytics import AnalyticsService

router = APIRouter(tags=["regions"])


@router.get("/regions")
async def get_regions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Region))
    regions = result.scalars().all()

    return [
        {
            "id": r.id,
            "code": r.code,
            "name": r.name,
            "type": r.type,
            "parent_id": r.parent_id,
        }
        for r in regions
    ]

