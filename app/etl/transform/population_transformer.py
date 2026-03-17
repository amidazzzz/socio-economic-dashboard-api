import pandas as pd


VALID_KEYWORDS = (
    "область",
    "край",
    "Республика",
    "автономный округ",
    "автономная область",
    "город федерального значения",
)


def is_subject(region_name: str) -> bool:
    return any(k in region_name for k in VALID_KEYWORDS)


async def transform_population(df: pd.DataFrame) -> list[dict]:
    df.columns = [
        "unit",
        "region",
        "2012",
        "2013",
        "2014",
        "2015",
        "2016",
        "2017",
    ]

    records: list[dict] = []

    year_columns = ["2012", "2013", "2014", "2015", "2016", "2017"]

    for _, row in df.iterrows():
        region = str(row["region"]).strip()

        if not is_subject(region):
            continue

        for year in year_columns:
            value = row[year]

            if pd.isna(value):
                continue

            records.append({
                "region_name": region,
                "year": int(year),
                "period": "year",
                "value": int(value),
                "source": "fedstat",
            })

    return records
