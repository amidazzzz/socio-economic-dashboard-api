import pandas as pd

from app.etl.contracts import IndicatorValueRecord


VALID_REGION_KEYWORDS = (
    "область",
    "край",
    "Республика",
    "автономный округ",
    "автономная область",
    "город",
)


def is_subject_region(region: str) -> bool:
    return any(keyword in region for keyword in VALID_REGION_KEYWORDS)


def normalize_year(value) -> int | None:
    if pd.isna(value):
        return None

    year_value = str(value).strip()
    if year_value.endswith(".0"):
        year_value = year_value[:-2]

    if year_value.isdigit() and len(year_value) == 4:
        return int(year_value)

    return None


def transform_simple_wide_indicator(
    df: pd.DataFrame,
    *,
    year_row_index: int,
    data_start_row_index: int,
    region_col_index: int,
    first_year_col_index: int,
    source: str = "fedstat",
    year_filter: set[int] | None = None,
) -> list[IndicatorValueRecord]:
    year_columns: list[tuple[int, int]] = []
    for column_index in range(first_year_col_index, len(df.columns)):
        year = normalize_year(df.iloc[year_row_index, column_index])
        if year is None:
            continue
        if year_filter is not None and year not in year_filter:
            continue
        year_columns.append((column_index, year))

    records: list[IndicatorValueRecord] = []
    for _, row in df.iloc[data_start_row_index:].iterrows():
        region = str(row.iloc[region_col_index]).strip()
        if not region or not is_subject_region(region):
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
                    "value": float(value),
                    "source": source,
                }
            )

    return records
