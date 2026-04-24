import pandas as pd

from app.etl.extract.readers import read_excel_async


async def extract_population_xls(path: str) -> pd.DataFrame:
    return await read_excel_async(path, header=0)
