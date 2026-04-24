import asyncio

from app.etl.extract.fedstat_natural_increase import extract_natural_increase_xls
from app.etl.job_runner import IndicatorETLJob, run_indicator_job
from app.etl.transform.natural_increase_transformer import (
    transform_natural_increase,
)


JOB = IndicatorETLJob(
    job_name="natural_increase",
    indicator_code="NATURAL_INCREASE",
    data_path="data/natural_increase.xls",
    extractor=extract_natural_increase_xls,
    transformer=transform_natural_increase,
)


async def run():
    return await run_indicator_job(JOB)


async def main():
    print(await run())


if __name__ == "__main__":
    asyncio.run(main())
