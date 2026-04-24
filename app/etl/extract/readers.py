import pandas as pd

from app.etl.utils import run_blocking


async def read_excel_async(path: str, **kwargs) -> pd.DataFrame:
    return await run_blocking(pd.read_excel, path, **kwargs)


async def read_csv_async(path: str, **kwargs) -> pd.DataFrame:
    return await run_blocking(pd.read_csv, path, **kwargs)
