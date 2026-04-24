import asyncio

from app.etl.job_runner import run_session_job
from app.etl.loader.unit_loader import load_units
from app.etl.loader.indicator_loader import load_indicators


async def run():
    units_result = await run_session_job("units", load_units)
    indicators_result = await run_session_job("indicators", load_indicators)
    return [units_result, indicators_result]


async def main():
    for result in await run():
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
