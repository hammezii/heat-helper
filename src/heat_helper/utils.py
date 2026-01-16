import os
import pandas as pd

from .exceptions import ColumnsNotUnique
from .core import _to_snake


# Utility Functions
def convert_col_snake_case(df: pd.DataFrame) -> pd.DataFrame:
    """_summary_

    Args:
        df (pd.DataFrame): _description_

    Raises:
        TypeError: _description_
        ColumnsNotUnique: _description_
        ColumnsNotUnique: _description_

    Returns:
        pd.DataFrame: _description_
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df must be a DataFrame, not {type(df).__name__}")

    columns = list(df.columns)

    if len(set(columns)) != len(columns):
        duplicates = set([x for x in columns if columns.count(x) > 1])
        raise ColumnsNotUnique(f"DataFrame has duplicate columns: {duplicates}")

    new_df = df.copy()
    new_cols = [_to_snake(c) for c in new_df.columns]
    if len(set(new_cols)) != len(new_cols):
        # Identify which names are duplicates for a better error message
        duplicates = set([x for x in new_cols if new_cols.count(x) > 1])
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

    Args:
        input_dir: The directory you want to get the filepaths from.
        print_to_terminal (optional): Defaults to False. Set to True if you want the terminal to print messages about the file processing.

    Raises:
        FileNotFoundError: Raises errors if the directory does not exist.

    Returns:
        List: A list of filepaths from the specified folder. Returns empty list if there are no Excel files in the folder.
    """

    # Helper function to control if messages are printed to terminal
    def log(message: str):
        if print_to_terminal:
            print(message)

    # Checks directory exists before function starts
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"The directory '{input_dir}' does not exist.")

    log(f"\nDiscovering files in '{input_dir}'")
    excel_files = 0
    filepaths = []  # empty list the filepaths will be added to
    # Iterate over all files in the given folder
    for filename in os.listdir(input_dir):  # for each file in the folder
        file_path = os.path.join(input_dir, filename)  # create the filepath
        # Check if it's an actual file and an Excel file
        if os.path.isfile(file_path) and filename.lower().endswith((".xlsx", ".xls")):
            excel_files += 1
            filepaths.append(file_path)  # add each filepath to the filepaths list
            log(f"  Found Excel file: {filename} and added to processing list.")
        else:
            log(f"  Skipping non-Excel file: {filename}")
    if not filepaths:
        log("No Excel files found to process.")
        return []
    return filepaths
