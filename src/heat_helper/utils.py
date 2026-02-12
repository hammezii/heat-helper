import os
import pandas as pd
from collections import Counter

from .exceptions import ColumnsNotUnique
from .core import _to_snake


# Utility Functions
def convert_col_snake_case(df: pd.DataFrame) -> pd.DataFrame:
    """Converts the column names of a DataFrame to snake case. 
    This function also checks for duplicate columns before and after conversion, 
    and raises a ColumnsNotUnique error if duplicates are found.

    Args:
        df: The DataFrame you want to convert the column names of to snake case.

    Raises:
        TypeError: Raises an error if the input is not a DataFrame.
        ColumnsNotUnique: Raises an error if there are duplicate columns in the original DataFrame or if the snake-case conversion results in duplicate column names. The error message will specify which columns are duplicated

    Returns:
        A new DataFrame with the same data but with column names converted to snake case.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df must be a DataFrame, not {type(df).__name__}")

    columns = list(df.columns)

    if len(set(columns)) != len(columns):
        counts = Counter(columns)
        duplicates = {x for x, count in counts.items() if count > 1}
        raise ColumnsNotUnique(f"DataFrame has duplicate columns: {duplicates}")

    new_df = df.copy()
    new_cols = [_to_snake(c) for c in new_df.columns]
    if len(set(new_cols)) != len(new_cols):
        # Identify which names are duplicates for a better error message
        counts_new = Counter(new_cols)
        duplicates = {x for x, count in counts_new.items() if count > 1}
        raise ColumnsNotUnique(
            f"Snake-case conversion created duplicate columns: {duplicates}"
        )

    new_df.columns = new_cols

    return new_df


# File Manipulation
def get_excel_filepaths_in_folder(
    input_dir: str, print_to_terminal: bool = False
) -> list[str]:
    """Returns a list of filepaths to Excel files (with the extension .xlsx or .xls) in a given folder.
    Note: Only searches the top-level of input_dir; does not recursively search subdirectories.

    Args:
        input_dir: The directory you want to get the filepaths from.
        print_to_terminal (optional): Defaults to False. Set to True if you want the terminal to print messages about the file processing.

    Raises:
        FileNotFoundError: Raises errors if the directory does not exist.

    Returns:
        A list of filepaths from the specified folder. Returns empty list if there are no Excel files in the folder.
    """

    # Helper function to control if messages are printed to terminal
    def log(message: str):
        if print_to_terminal:
            print(message)

    # Checks directory exists before function starts
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"The directory '{input_dir}' does not exist.")

    log(f"\nDiscovering files in '{input_dir}'")
    filepaths = []  # empty list the filepaths will be added to
    # Iterate over all files in the given folder
    for filename in os.listdir(input_dir):  # for each file in the folder
        file_path = os.path.join(input_dir, filename)  # create the filepath
        # Check if it's an actual file and an Excel file
        if os.path.isfile(file_path) and filename.lower().endswith((".xlsx", ".xls")):
            filepaths.append(file_path)  # add each filepath to the filepaths list
            log(f"  Found Excel file: {filename} and added to processing list.")
        else:
            log(f"  Skipping non-Excel file: {filename}")
    if not filepaths:
        log("No Excel files found to process.")
        return []
    return filepaths
