import asyncio
from app.core.database import AsyncSessionLocal
from app.etl.loader.unit_loader import load_units
from app.etl.loader.indicator_loader import load_indicators


async def main():
    async with AsyncSessionLocal() as db:
        # await load_units(db)
        await load_indicators(db)


if __name__ == "__main__":
    asyncio.run(main())
