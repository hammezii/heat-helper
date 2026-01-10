import pandas as pd
from heat_helper.exceptions import ColumnDoesNotExistError


def get_updates(df: pd.DataFrame, new_col: str, heat_col: str) -> pd.Series:
    """Compares two DataFrame columns and returns a value if new_col is different to heat_col.
    This can help you identify where new data is different to existing HEAT records and therefore needs updating.
    It returns a new column which only contains data that needs to be updated - so it can be copied to the HEAT import template.

    Args:
        df (pd.DataFrame): DataFrame where the columns are located.
        new_col (str): The column which contains 'new' data. This would be the data you want to update on HEAT if it differs from values in heat_col.
        heat_col (str): The corresponding column in your HEAT export e.g. if you are checking if any postcodes need updating, both new_col and heat_col should contain postcodes.

    Raises:
        TypeError: Raised if df is not a DataFrame or new_col and heat_col are not strings (text).
        ColumnDoesNotExistError: Raised if either new_col or heat_col are not in df columns.

    Returns:
        A DataFrame column where rows contain the value from new_col if this is different to heat_col.
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
            raise ColumnDoesNotExistError(f"'{col}' not found in {df} column list.")

    left = df[new_col]
    right = df[heat_col]

    # Warning if dtypes are different
    if left.dtype != right.dtype:
        print(
            f"WARNING: Type Mismatch: {new_col} is {left.dtype}, but {heat_col} is {right.dtype}"
        )

    # Standard equality check that handles nulls
    condition = ~(left.eq(right) | (left.isna() & right.isna()))

    # Return updated data if True, otherwise return null
    update_col = df[new_col].where(condition, other=pd.NA)  # type: ignore

    return update_col


def get_contextual_updates(
    df: pd.DataFrame, new_col: str, heat_col: str, bad_values: list[str]
) -> pd.Series:
    """This function is similar to get_updates, except you can also pass a list of 'bad' values you do not want to override HEAT data.
    This can be useful if you want to ensure that data like 'Not available' or 'Unknown' does not overwrite previously collected 'good' values in the contextual data columns.

    Args:
        df (pd.DataFrame): DataFrame where the columns are located.
        new_col (str): The column which contains 'new' data. This would be the data you want to update on HEAT if it differs from values in heat_col.
        heat_col (str): The corresponding column in your HEAT export e.g. if you are checking if any postcodes need updating, both new_col and heat_col should contain postcodes.
        bad_values (list[str]): A list of values which should not overwrite 'good' data in your HEAT records. For example, if your new data contains 'Not available' or 'Unknown' but your HEAT records had values in these columns, you could pass ['Not available', 'Unknown'] to this variable, and these will not overwrite 'good' values in the heat_col.

    Raises:
        TypeError: Raised if df is not a DataFrame, new_col and heat_col are not strings (text), or bad_values is not a list.
        ColumnDoesNotExistError: Raised if either new_col or heat_col are not in df columns.

    Returns:
        A DataFrame column where rows contain the value from new_col if this is different to heat_col.
    """
    # Type checking
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"{df} must be a DataFrame.")
    if not isinstance(new_col, str):
        raise TypeError(f"Text must be a string, not {type(new_col).__name__}")
    if not isinstance(heat_col, str):
        raise TypeError(f"Text must be a string, not {type(heat_col).__name__}")
    if not isinstance(bad_values, list):
        raise TypeError(f"{bad_values} must be a List.")

    for col in [new_col, heat_col]:
        if col not in df.columns:
            raise ColumnDoesNotExistError(f"'{col}' not found in {df} column list.")

    left = df[new_col]
    right = df[heat_col]

    # Warning if dtypes are different
    if left.dtype != right.dtype:
        print(
            f"WARNING: Type Mismatch: {new_col} is {left.dtype}, but {heat_col} is {right.dtype}"
        )

    # Define Update conditions: if values are different and left is not a bad_value
    left_good = ~left.isin(bad_values) & left.notna()
    is_different = ~(left.eq(right) | (left.isna() & right.isna()))
    condition = is_different & left_good

    update_col = df[new_col].where(condition, other=pd.NA)  # type: ignore

    return update_col
