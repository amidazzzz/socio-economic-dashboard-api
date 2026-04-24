import asyncio

from app.etl.extract.fedstat_unemployment import extract_unemployment_xls
from app.etl.job_runner import IndicatorETLJob, run_indicator_job
from app.etl.transform.unemployment_transformer import transform_unemployment


JOB = IndicatorETLJob(
    job_name="unemployment",
    indicator_code="UNEMPLOYMENT_RATE",
    data_path="data/unemployment.xls",
    extractor=extract_unemployment_xls,
    transformer=transform_unemployment,
)


async def run():
    return await run_indicator_job(JOB)


async def main():
    print(await run())


if __name__ == "__main__":
    asyncio.run(main())
