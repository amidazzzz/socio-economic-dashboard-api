import asyncio

from app.etl.extract.fedstat_vrp import extract_vrp_xls
from app.etl.job_runner import IndicatorETLJob, run_indicator_job
from app.etl.transform.vrp_transformer import transform_vrp


JOB = IndicatorETLJob(
    job_name="vrp",
    indicator_code="VRP_TOTAL",
    data_path="data/vrp.xls",
    extractor=extract_vrp_xls,
    transformer=transform_vrp,
)


async def run():
    return await run_indicator_job(JOB)


async def main():
    print(await run())


if __name__ == "__main__":
    asyncio.run(main())
