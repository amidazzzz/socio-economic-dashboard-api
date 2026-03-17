import pandas as pd
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

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


async def load_regions(session: AsyncSession) -> None:
    df = pd.read_csv(
        OKATO_PATH,
        sep=";",
        dtype=str,
        encoding="cp1251"
    )

    df.fillna("000")

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

    regions = [
        Region(
            code=row["code"],
            name=row["name"].strip(),
            type=detect_region_type(row["name"]),
            parent_id=None,
        )
        for _, row in regions_df.iterrows()
    ]

    await session.execute(delete(Region))
    session.add_all(regions)
    await session.commit()

    print(f"[ETL] Загружено субъектов РФ: {len(regions)}")
