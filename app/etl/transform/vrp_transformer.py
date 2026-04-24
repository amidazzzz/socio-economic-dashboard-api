import pandas as pd

from app.etl.contracts import IndicatorValueRecord
from app.etl.transform.shared import is_subject_region, normalize_year


def transform_vrp(df: pd.DataFrame) -> list[IndicatorValueRecord]:
    year_columns: list[tuple[int, int]] = []
    for column_index in range(3, len(df.columns)):
        year = normalize_year(df.iloc[2, column_index])
        if year is None:
            continue
        year_columns.append((column_index, year))

    records: list[IndicatorValueRecord] = []
    for _, row in df.iloc[3:].iterrows():
        section = str(row.iloc[0]).strip()
        region = str(row.iloc[1]).strip()

        if section != "Всего" or not region or not is_subject_region(region):
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
                    "source": "fedstat",
                }
            )

    return records
