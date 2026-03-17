import asyncio
from app.core.database import AsyncSessionLocal
from app.etl.loader.region_loader import load_regions


async def main():
    async with AsyncSessionLocal() as db:
        await load_regions(db)


if __name__ == "__main__":
    asyncio.run(main())
