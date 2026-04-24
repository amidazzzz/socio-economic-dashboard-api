import asyncio

from app.etl.extract.fedstat_average_salary import extract_average_salary_xls
from app.etl.job_runner import IndicatorETLJob, run_indicator_job
from app.etl.transform.average_salary_transformer import transform_average_salary


JOB = IndicatorETLJob(
    job_name="average_salary",
    indicator_code="AVERAGE_SALARY_REAL_INDEX",
    data_path="data/average_salary.xls",
    extractor=extract_average_salary_xls,
    transformer=transform_average_salary,
)


async def run():
    return await run_indicator_job(JOB)


async def main():
    print(await run())


if __name__ == "__main__":
    asyncio.run(main())
