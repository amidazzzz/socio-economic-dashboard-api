import asyncio

from app.etl.job_runner import run_session_job
from app.etl.loader.region_loader import load_regions


async def run():
    return await run_session_job("regions", load_regions)


async def main():
    print(await run())


if __name__ == "__main__":
    asyncio.run(main())
