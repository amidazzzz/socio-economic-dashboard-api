from collections.abc import Awaitable, Callable
from importlib import import_module

from app.etl.contracts import ETLJobResult

JobRunner = Callable[[], Awaitable[ETLJobResult | list[ETLJobResult]]]

JOB_IMPORTS: dict[str, tuple[str, str]] = {
    "bootstrap": ("app.etl.jobs.indicator_and_unit", "run"),
    "regions": ("app.etl.jobs.region", "run"),
    "average_salary": ("app.etl.jobs.average_salary", "run"),
    "migration_balance": ("app.etl.jobs.migration_balance", "run"),
    "population": ("app.etl.jobs.population", "run"),
    "natural_increase": ("app.etl.jobs.natural_increase", "run"),
    "unemployment": ("app.etl.jobs.unemployment", "run"),
    "vrp": ("app.etl.jobs.vrp", "run"),
}

PIPELINES: dict[str, list[str]] = {
    "all": [
        "bootstrap",
        "regions",
        "population",
        "natural_increase",
        "migration_balance",
        "average_salary",
        "vrp",
        "unemployment",
    ],
}


def get_available_job_names() -> list[str]:
    return sorted([*JOB_IMPORTS.keys(), *PIPELINES.keys()])


def resolve_job_runner(name: str) -> JobRunner:
    if name not in JOB_IMPORTS:
        available = ", ".join(get_available_job_names())
        raise ValueError(f"Unknown ETL job '{name}'. Available jobs: {available}")

    module_name, attr_name = JOB_IMPORTS[name]
    module = import_module(module_name)
    return getattr(module, attr_name)


async def run_job(name: str) -> list[ETLJobResult]:
    if name in PIPELINES:
        results: list[ETLJobResult] = []
        for job_name in PIPELINES[name]:
            results.extend(await run_job(job_name))
        return results

    runner = resolve_job_runner(name)
    result = await runner()
    if isinstance(result, list):
        return result
    return [result]
