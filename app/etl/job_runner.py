from dataclasses import dataclass
from typing import Awaitable, Callable

import pandas as pd

from app.core.database import AsyncSessionLocal
from app.etl.contracts import ETLJobResult, IndicatorValueRecord
from app.etl.loader.indicator_value_loader import load_indicator_values

Extractor = Callable[[str], Awaitable[pd.DataFrame]]
Transformer = Callable[[pd.DataFrame], list[IndicatorValueRecord]]
SessionJobRunner = Callable[..., Awaitable[int]]


@dataclass(slots=True)
class IndicatorETLJob:
    job_name: str
    indicator_code: str
    data_path: str
    extractor: Extractor
    transformer: Transformer


async def run_indicator_job(job: IndicatorETLJob) -> ETLJobResult:
    dataframe = await job.extractor(job.data_path)
    records = job.transformer(dataframe)

    async with AsyncSessionLocal() as session:
        loaded_rows = await load_indicator_values(
            session=session,
            indicator_code=job.indicator_code,
            records=records,
        )

    return ETLJobResult(
        job_name=job.job_name,
        extracted_rows=len(dataframe),
        transformed_rows=len(records),
        loaded_rows=loaded_rows,
    )


async def run_session_job(
    job_name: str,
    runner: SessionJobRunner,
    *args,
    **kwargs,
) -> ETLJobResult:
    async with AsyncSessionLocal() as session:
        loaded_rows = await runner(session, *args, **kwargs)

    return ETLJobResult(
        job_name=job_name,
        loaded_rows=loaded_rows,
    )
