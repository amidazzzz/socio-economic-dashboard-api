import pandas as pd

from app.etl.extract.readers import read_excel_async


async def extract_natural_increase_xls(path: str) -> pd.DataFrame:
    return await read_excel_async(path, header=None)
