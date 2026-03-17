import pandas as pd
import asyncio

async def extract_population_xls(path: str) -> pd.DataFrame:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        lambda: pd.read_excel(path, header=0))