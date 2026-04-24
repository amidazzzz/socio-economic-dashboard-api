import pandas as pd

from app.etl.contracts import IndicatorValueRecord
from app.etl.transform.shared import transform_simple_wide_indicator


def transform_migration_balance(df: pd.DataFrame) -> list[IndicatorValueRecord]:
    return transform_simple_wide_indicator(
        df,
        year_row_index=2,
        data_start_row_index=3,
        region_col_index=0,
        first_year_col_index=1,
    )
