import asyncio

from app.core.database import AsyncSessionLocal
from app.etl.extract.fedstat_population import extract_population_xls
from app.etl.transform.population_transformer import transform_population
from app.etl.loader.indicator_value_loader import load_indicator_values


DATA_PATH = "data/population.xls"


async def main():
    df = await extract_population_xls(DATA_PATH)
    records = await transform_population(df)

    async with AsyncSessionLocal() as db:
        await load_indicator_values(
            session=db,
            indicator_code="POPULATION_TOTAL",
            records=records,
        )


if __name__ == "__main__":
    asyncio.run(main())
