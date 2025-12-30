# Import internal libraries
from datetime import date
import re
import os

#Import external libraries

#Import helper functions
from .exceptions import InvalidYearGroupError, FELevelError

# Constants defined at module level for performance
RECEPTION_ALIASES = {"reception", "r", "year r", "rec", "year group r", "y0", "year 0"}
POSTCODE_REGEX = r"^[A-Z]{1,2}[0-9][A-Z0-9]? [0-9][A-Z]{2}$"


# Helper functions for main functions
def _parse_year_group_to_int(year_group: str | int) -> int:
    """Internal helper to convert any year group input to an integer (0-13)."""
    if isinstance(year_group, str):
        if 'Level' in year_group:
            raise FELevelError(year_group)
        clean_input = year_group.strip().lower()
        if clean_input in RECEPTION_ALIASES:
            return 0
        match = re.search(r"\d+", clean_input)
        if not match:
            raise InvalidYearGroupError(year_group)
        y_num = int(match.group())
    else:
        if isinstance(year_group, int):
            y_num = year_group

    if not (0 <= y_num <= 13):
        raise InvalidYearGroupError(year_group)
    return y_num

def _string_contains_int(string: str) -> bool:
    match = re.search(r"[0-9]+", string)
    if not match:
        return False
    else:
        return True

# Main functions for file manipulation
def get_excel_filepaths_in_folder(input_dir: str, print_to_terminal: bool = False) -> list[str]:
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
