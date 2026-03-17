import pandas as pd

VALID_KEYWORDS = (
    "область",
    "край",
    "Республика",
    "автономный округ",
    "автономная область",
    "город",
)

def is_subject(region: str) -> bool:
    return any(k in region for k in VALID_KEYWORDS)

def parse_value(value):
    if pd.isna(value):
        return None
    return float(str(value).replace(",", "."))

def find_year_value_columns(df: pd.DataFrame) -> dict[int, int]:
    year_row = None
    label_row = None

    for i in range(10):
        row = df.iloc[i].astype(str)

        if any("значение показателя за год" in v for v in row):
            label_row = i

        if any(v.strip().isdigit() and len(v.strip()) == 4 for v in row):
            year_row = i

    if year_row is None or label_row is None:
        raise ValueError("Не найдены строки заголовков")

    mapping = {}

    for col_idx, label in enumerate(df.iloc[label_row]):
        if "значение показателя за год" not in str(label):
            continue

        # ищем год влево
        year = None
        for back in range(col_idx, -1, -1):
            val = df.iloc[year_row, back]
            if pd.notna(val) and str(val).strip().isdigit():
                year = int(val)
                break

        if year is None:
            continue  # безопасно пропускаем

        mapping[col_idx] = year

    return mapping

def transform_unemployment(df: pd.DataFrame) -> list[dict]:
    records = []

    year_cols = find_year_value_columns(df)

    for _, row in df.iterrows():
        age_group = str(row.iloc[0]).strip()
        region = str(row.iloc[1]).strip()

        if age_group != "15-72 лет":
            continue
        if not is_subject(region):
            continue

        ALLOWED_YEARS = set(range(2000, 2024))

        for col_idx, year in year_cols.items():
            if year not in ALLOWED_YEARS:
                continue

            value = parse_value(row.iloc[col_idx])
            if value is None:
                continue

            records.append({
                "region_name": region,
                "year": year,
                "period": "year",
                "value": value,
                "source": "fedstat",
            })

    return records

