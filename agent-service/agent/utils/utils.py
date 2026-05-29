import pandas as pd


def get_longest_label(df: pd.DataFrame) -> int:
    """Return length of longest string value across all string columns."""
    str_cols = df.select_dtypes(include=["object", "str"]).columns
    if len(str_cols) == 0:
        return 0
    return int(df[str_cols].apply(lambda col: col.astype(str).str.len().max()).max())
