import re
from datetime import date
import pandas as pd


# Import helper functions
from heat_helper.exceptions import InvalidYearGroupError, FELevelError


# Get CURRENT_ACADEMIC_YEAR_START constant function defined here apart from others due to constant below
def _calc_current_academic_year_start(date_now: date) -> int:
    if date_now.month in [9, 10, 11, 12]:
        return date_now.year
    else:
        return date_now.year - 1


# CONSTANTS
# Used in clean year groups
RECEPTION_ALIASES = {"reception", "r", "year r", "rec", "year group r", "y0", "year 0"}

# Used to validated postcode format
POSTCODE_REGEX = r"^[A-Z]{1,2}[0-9][A-Z0-9]? [0-9][A-Z]{2}$"

# Used to calculate current academic year for year group / date maniuplation functions
CURRENT_ACADEMIC_YEAR_START = _calc_current_academic_year_start(date.today())

# Used to remove punctuation except hyphens and apostrophes
PUNCTUATION = '!@#£$%^&*()_=+`~,.<>/?;:"\\|[]'

# For matching functions
STUDENT_HEAT_ID = "Student HEAT ID"


# Helper functions for main functions
def _parse_year_group_to_int(year_group: str | int | pd.Series) -> int:
    """Internal helper to convert any year group input to an integer (0-13)."""
    if isinstance(year_group, pd.Series):
        return year_group.apply(_parse_year_group_to_int)
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
    elif isinstance(year_group, int):
        y_num = year_group
    else:
        raise TypeError(f"Input must be str or int, not {type(year_group).__name__}")

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


def _to_snake(name: str) -> str:
    # 1. Handle CamelCase (e.g., FirstName -> First_Name)
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name.strip())
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)

    # 2. Remove special characters (keep only alphanumeric and spaces)
    clean = re.sub(r"[^a-zA-Z0-9\s_]", "", s2)

    # 3. Collapse whitespace, lower, and underscore
    return re.sub(r"[_\s]+", "_", clean.strip()).lower()