import asyncio

from app.core.database import AsyncSessionLocal
from app.etl.extract.fedstat_unemployment import extract_unemployment_xls
from app.etl.transform.unemployment_transformer import transform_unemployment
from app.etl.loader.indicator_value_loader import load_indicator_values


DATA_PATH = "data/unemployment.xls"
INDICATOR_CODE = "UNEMPLOYMENT_RATE"


async def main():
    df_raw = await extract_unemployment_xls(DATA_PATH)
    records = transform_unemployment(df_raw)
    print(f"records count = {len(records)}")
    print(records[:5])

    async with AsyncSessionLocal() as session:
        await load_indicator_values(
            session=session,
            indicator_code=INDICATOR_CODE,
            records=records,
        )


if __name__ == "__main__":
    asyncio.run(main())
