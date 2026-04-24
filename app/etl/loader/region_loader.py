import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from app.etl.extract.readers import read_csv_async
from app.model.region import Region


OKATO_PATH = "data/okato.csv"


REGION_TYPES = {
    "республика": "republic",
    "край": "krai",
    "область": "oblast",
    "автономный округ": "autonomous okrug",
    "автономная область": "autonomous oblast",
    "г ": "federal city",
}


def detect_region_type(name: str) -> str:
    name_l = name.lower()
    for key, value in REGION_TYPES.items():
        if key in name_l:
            return value
    return "other"


async def load_regions(session: AsyncSession, path: str = OKATO_PATH) -> int:
    df = await read_csv_async(
        path,
        sep=";",
        dtype=str,
        encoding="cp1251"
    )

    df = df.fillna("000")

    df = df.rename(columns={
        "00": "region_code",
        "000": "district_code",
        "000.1": "city_code",
        "000.2": "settlement_code",
        "Объекты административно-территориального деления,^ кроме сельских населенных пунктов": "name",
    })

    regions_df = df[
        (df["region_code"] != "00") &
        (df["district_code"] == "000") &
        (df["city_code"] == "000") &
        (df["settlement_code"] == "000")
    ].copy()

    regions_df["code"] = regions_df["region_code"] + "000000000"

    regions_df = regions_df[
        ~regions_df["name"].str.contains("Сириус", case=False, na=False)
    ]

    regions_df = regions_df.drop_duplicates(subset=["code"], keep="first")

    synced = 0
    for _, row in regions_df.iterrows():
        region_name = row["name"].strip()
        stmt = (
            insert(Region)
            .values(
                code=row["code"],
                name=region_name,
                type=detect_region_type(region_name),
                parent_id=None,
            )
            .on_conflict_do_update(
                index_elements=["code"],
                set_={
                    "name": region_name,
                    "type": detect_region_type(region_name),
                    "parent_id": None,
                },
            )
        )
        await session.execute(stmt)
        synced += 1

    await session.commit()

    print(f"[ETL] Синхронизировано субъектов РФ: {synced}")
    return synced
