import asyncio

from app.etl.extract.fedstat_population import extract_population_xls
from app.etl.job_runner import IndicatorETLJob, run_indicator_job
from app.etl.transform.population_transformer import transform_population


JOB = IndicatorETLJob(
    job_name="population",
    indicator_code="POPULATION_TOTAL",
    data_path="data/population.xls",
    extractor=extract_population_xls,
    transformer=transform_population,
)


async def run():
    return await run_indicator_job(JOB)


async def main():
    print(await run())


if __name__ == "__main__":
    asyncio.run(main())
