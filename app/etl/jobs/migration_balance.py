import asyncio

from app.etl.extract.fedstat_migration_balance import (
    extract_migration_balance_xls,
)
from app.etl.job_runner import IndicatorETLJob, run_indicator_job
from app.etl.transform.migration_balance_transformer import (
    transform_migration_balance,
)


JOB = IndicatorETLJob(
    job_name="migration_balance",
    indicator_code="MIGRATION_BALANCE_RATE",
    data_path="data/migration_balance.xls",
    extractor=extract_migration_balance_xls,
    transformer=transform_migration_balance,
)


async def run():
    return await run_indicator_job(JOB)


async def main():
    print(await run())


if __name__ == "__main__":
    asyncio.run(main())
