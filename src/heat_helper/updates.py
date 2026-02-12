import pandas as pd
from heat_helper.exceptions import ColumnDoesNotExistError
from collections.abc import Iterable


def get_updates(df: pd.DataFrame, new_col: str, heat_col: str) -> pd.Series:
    """Compares two DataFrame columns and returns a value if new_col is different to heat_col.
    This can help you identify where new data is different to existing HEAT records and therefore needs updating.
    It returns a new column which only contains data that needs to be updated - so it can be copied to the HEAT import template.
    The original DataFrame is not modified; a copy is created internally.

    Args:
        df (pd.DataFrame): DataFrame where the columns are located.
        new_col (str): The column which contains 'new' data. This would be the data you want to update on HEAT if it differs from values in heat_col.
        heat_col (str): The corresponding column in your HEAT export e.g. if you are checking if any postcodes need updating, both new_col and heat_col should contain postcodes.

    Raises:
        TypeError: Raised if df is not a DataFrame or new_col and heat_col are not strings (text).
        ColumnDoesNotExistError: Raised if either new_col or heat_col are not in df columns.

    Returns:
        A pandas Series (DataFrame column) where rows contain the value from new_col if this is different to heat_col.
    """
    # Type checking
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"{df} must be a DataFrame.")
    if not isinstance(new_col, str):
        raise TypeError(f"Text must be a string, not {type(new_col).__name__}")
    if not isinstance(heat_col, str):
        raise TypeError(f"Text must be a string, not {type(heat_col).__name__}")

    for col in [new_col, heat_col]:
        if col not in df.columns:
            raise ColumnDoesNotExistError(
                f"'{col}' not found in DataFrame column list."
            )

    df_copy = df.copy() # Create a copy of the DataFrame to avoid modifying the original
    left = df_copy[new_col]
    right = df_copy[heat_col]

    # Warning if dtypes are different
    if left.dtype != right.dtype:
        print(
            f"WARNING: Type Mismatch: {new_col} is {left.dtype}, but {heat_col} is {right.dtype}"
        )

    # Standard equality check that handles nulls
    condition = ~(left.eq(right) | (left.isna() & right.isna()))

    # Fill blank strings with None, then return updated data if True, otherwise return null
    if left.dtype == "object":
        df_copy[new_col] = df_copy[new_col].fillna("").replace(r"^\s*$", None, regex=True)
    update_col = df_copy[new_col].where(condition, other=None)  # type: ignore

    return update_col


def get_contextual_updates(
    df: pd.DataFrame, new_col: str, heat_col: str, bad_values: Iterable[str]
) -> pd.Series:
    """This function is similar to get_updates, except you can also pass a list, set, tuple or other Iterable of 'bad' values you do not want to override HEAT data.
    This can be useful if you want to ensure that data like 'Not available' or 'Unknown' does not overwrite previously collected 'good' values in the contextual data columns.
    The original DataFrame is not modified; a copy is created internally.

    Args:
        df (pd.DataFrame): DataFrame where the columns are located.
        new_col (str): The column which contains 'new' data. This would be the data you want to update on HEAT if it differs from values in heat_col.
        heat_col (str): The corresponding column in your HEAT export e.g. if you are checking if any postcodes need updating, both new_col and heat_col should contain postcodes.
        bad_values (Iterable[str]): A list, tuple, or set (or other Iterable) of values which should not overwrite 'good' data in your HEAT records. For example, if your new data contains 'Not available' or 'Unknown' but your HEAT records had values in these columns, you could pass ['Not available', 'Unknown'] to this variable, and these will not overwrite 'good' values in the heat_col.

    Raises:
        TypeError: Raised if df is not a DataFrame, new_col and heat_col are not strings (text), or bad_values is not a list.
        ColumnDoesNotExistError: Raised if either new_col or heat_col are not in df columns.

    Returns:
        A pandas Series (DataFrame column) where rows contain the value from new_col if this is different to heat_col.
    """
    # Type checking
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"{df} must be a DataFrame.")
    if not isinstance(new_col, str):
        raise TypeError(f"Text must be a string, not {type(new_col).__name__}")
    if not isinstance(heat_col, str):
        raise TypeError(f"Text must be a string, not {type(heat_col).__name__}")
    if not isinstance(bad_values, Iterable) or isinstance(bad_values, str):
        raise TypeError(f"{bad_values} must be Iterable: e.g. list, tuple, set.")

    for col in [new_col, heat_col]:
        if col not in df.columns:
            raise ColumnDoesNotExistError(f"'{col}' not found in {df} column list.")

    df_copy = df.copy() # Create a copy of the DataFrame to avoid modifying the original
    left = df_copy[new_col]
    right = df_copy[heat_col]

    # Warning if dtypes are different
    if left.dtype != right.dtype:
        print(
            f"WARNING: Type Mismatch: {new_col} is {left.dtype}, but {heat_col} is {right.dtype}"
        )

    bad_values_set = set(bad_values) if not isinstance(bad_values, set) else bad_values

    # Define Update conditions: if values are different and left is not a bad_value
    left_good = ~left.isin(bad_values_set) & left.notna()
    is_different = ~(left.eq(right) | (left.isna() & right.isna()))
    condition = is_different & left_good

    if left.dtype == "object":
        df_copy[new_col] = df_copy[new_col].fillna("").replace(r"^\s*$", None, regex=True)
    update_col = df_copy[new_col].where(condition, other=None)  # type: ignore

    return update_col
