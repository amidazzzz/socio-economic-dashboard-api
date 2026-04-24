import argparse
import asyncio

from app.etl.registry import get_available_job_names, run_job


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run ETL jobs")
    parser.add_argument(
        "job",
        nargs="?",
        default="all",
        help="Job name to run",
        choices=get_available_job_names(),
    )
    return parser


async def _main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    results = await run_job(args.job)
    for result in results:
        print(result)


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
