
#Import helper functions
from .exceptions import InvalidYearGroupError
from .core import _parse_year_group_to_int

def clean_year_group(
    year_group: str | int, errors: str = "raise"
) -> str | None:
    """Takes school year groups and cleans them to have the consistent format 'Year i'.

    Args:
        year_group: Text you wish to clean. Numbers entered will be cast to strings if possible.
        errors: default = 'raise' which raises all errors. 'ignore' returns original value, 'coerce' returns None.

    Raises:
        InvalidYearGroupError: Raised when the year group input cannot be parsed or is out of range.
        SchoolYearError: Raised when year_group is not a valid string.

    Returns:
        Cleaned year group in the format 'Year i'.
    """
    try:
        y_num = _parse_year_group_to_int(year_group)
        return "Reception" if y_num == 0 else f"Year {y_num}"
    except (InvalidYearGroupError, TypeError, ValueError):
        if errors == "ignore":
            return str(year_group)
        if errors == "coerce":
            return None
        raise