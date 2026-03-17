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


def extract_year_columns(df: pd.DataFrame) -> list[tuple[str, int]]:
    if len(df) < 2:
        return []

    year_row = df.iloc[1]
    year_columns: list[tuple[str, int]] = []

    for column_name in df.columns[2:]:
        value = year_row[column_name]
        if pd.isna(value):
            continue

        value_str = str(value).strip()
        if value_str.isdigit() and len(value_str) == 4:
            year_columns.append((column_name, int(value_str)))

    return year_columns


async def transform_population(df: pd.DataFrame) -> list[dict]:
    renamed_columns = list(df.columns)
    renamed_columns[0] = "unit"
    renamed_columns[1] = "region"
    df.columns = renamed_columns

    records: list[dict] = []
    year_columns = extract_year_columns(df)

    for _, row in df.iterrows():
        region = str(row["region"]).strip()

        if not is_subject(region):
            continue

        for column_name, year in year_columns:
            value = row[column_name]

            if pd.isna(value):
                continue

            records.append({
                "region_name": region,
                "year": year,
                "period": "year",
                "value": int(value),
                "source": "fedstat",
            })

    return records
