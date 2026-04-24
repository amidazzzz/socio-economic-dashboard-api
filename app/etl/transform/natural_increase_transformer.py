import pandas as pd

from app.etl.contracts import IndicatorValueRecord


VALID_KEYWORDS = (
    "область",
    "край",
    "Республика",
    "автономный округ",
    "автономная область",
    "город",
)


def is_subject(region: str) -> bool:
    return any(keyword in region for keyword in VALID_KEYWORDS)


def extract_year_columns(df: pd.DataFrame) -> list[tuple[int, int]]:
    year_columns: list[tuple[int, int]] = []

    for column_index, value in enumerate(df.iloc[2]):
        if pd.isna(value):
            continue

        year_value = str(value).strip()
        if year_value.endswith(".0"):
            year_value = year_value[:-2]

        if year_value.isdigit() and len(year_value) == 4:
            year_columns.append((column_index, int(year_value)))

    return year_columns


def transform_natural_increase(df: pd.DataFrame) -> list[IndicatorValueRecord]:
    records: list[IndicatorValueRecord] = []
    year_columns = extract_year_columns(df)

    for _, row in df.iloc[3:].iterrows():
        region = str(row.iloc[0]).strip()

        if not region or not is_subject(region):
            continue

        for column_index, year in year_columns:
            value = row.iloc[column_index]
            if pd.isna(value):
                continue

            records.append(
                {
                    "region_name": region,
                    "year": year,
                    "period": "year",
                    "value": int(value),
                    "source": "fedstat",
                }
            )

    return records
