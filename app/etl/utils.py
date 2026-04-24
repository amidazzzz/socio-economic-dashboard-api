import asyncio
from functools import partial
from typing import Any


async def run_blocking(func, /, *args, **kwargs) -> Any:
    loop = asyncio.get_running_loop()
    bound = partial(func, *args, **kwargs)
    return await loop.run_in_executor(None, bound)
