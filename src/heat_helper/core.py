# Import internal libraries
import re
import os
from datetime import date

# Import external libraries

# Import helper functions
from heat_helper.exceptions import InvalidYearGroupError, FELevelError


# Get CURRENT_ACADEMIC_YEAR_START constant
def _calc_current_academic_year_start(date_now: date) -> int:
    if date_now.month in [9, 10, 11, 12]:
        return date_now.year
    else:
        return date_now.year - 1


# Constants defined at module level for performance
RECEPTION_ALIASES = {"reception", "r", "year r", "rec", "year group r", "y0", "year 0"}
POSTCODE_REGEX = r"^[A-Z]{1,2}[0-9][A-Z0-9]? [0-9][A-Z]{2}$"
CURRENT_ACADEMIC_YEAR_START = _calc_current_academic_year_start(date.today())


# Helper functions for main functions
def _parse_year_group_to_int(year_group: str | int) -> int:
    """Internal helper to convert any year group input to an integer (0-13)."""
    if isinstance(year_group, str):
        if "level" in year_group.lower():
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
    
def _is_valid_postcode(postcode: str) -> bool:
    """Checks if a string is a validly formatted UK postcode. Does not check a postcode exists.
    Matches formats: A9 9AA, A99 9AA, AA9 9AA, AA99 9AA, A9A 9AA, AA9A 9AA.

    Args:
        postcode: the postcode to pattern match.

    Returns:
        True/False
    """
    if not isinstance(postcode, str):
        return False

    # If it's too short to even be a postcode, fail fast
    if len(postcode) < 5:
        return False

    # Check against the Regex
    return bool(re.match(POSTCODE_REGEX, postcode))


# Main functions for file manipulation
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
