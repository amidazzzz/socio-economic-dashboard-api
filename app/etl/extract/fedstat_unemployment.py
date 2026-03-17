import asyncio
import pandas as pd


async def extract_unemployment_xls(path: str) -> pd.DataFrame:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        lambda: pd.read_excel(path, header=None)
    )
