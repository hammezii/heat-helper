# Internal python libraries
from datetime import date

# Import helper functions
from heat_helper.exceptions import InvalidYearGroupError
from heat_helper.core import _parse_year_group_to_int, CURRENT_ACADEMIC_YEAR_START


def clean_year_group(year_group: str | int, errors: str = "raise") -> str | None:
    """Takes school year groups and cleans them to have the consistent format 'Year i'.

    Args:
        year_group: Text you wish to clean. Numbers entered will be cast to strings if possible.
        errors: default = 'raise' which raises all errors. 'ignore' returns original value, 'coerce' returns None.

    Raises:
        InvalidYearGroupError: Raised when `year group` input cannot be parsed or is out of range.
        TypeError: Raised when `year group` input cannot be parsed to a valid int.

    Returns:
        Cleaned year group in the format 'Year i'.
    """
    try:
        y_num = _parse_year_group_to_int(year_group)
        return "Reception" if y_num == 0 else f"Year {y_num}"
    except (InvalidYearGroupError, TypeError):
        if errors == "ignore":
            return str(year_group)
        if errors == "coerce":
            return None
        raise


def calculate_year_group_from_date(
    input_date: date,
    start_of_academic_year: int = CURRENT_ACADEMIC_YEAR_START,
    errors: str = "raise",
) -> str | None:
    """Calculates school year group from date of birth for the English school system. Returns 'Year i' or 'Reception', or 'Student too young for school' if date of birth is not of school age.

    Args:
        input_date: Date of birth you wish to know the school year for.
        start_of_academic_year (optional): The school year in which you want to calculate the year group for. Allows you to calculate a year group for any academic year not just current e.g. for 2025/26 school year enter 2025. Default is start of current academic year.
        errors (optional): default = 'raise' which raises all errors. 'ignore' returns None.

    Raises:
        TypeError: Raised if input_date is not a date.
        InvalidYearGroupError: Raised when the calculated year group is out of range (greater than Year 13).

    Returns:
        Returns 'Year i', 'Reception', 'Student too young for school' or None if errors='ignore'.
    """
    try:
        if not isinstance(input_date, date):
            raise TypeError(f"Input must be a date, not {type(input_date).__name__}")
        if input_date.month in [9, 10, 11, 12]:
            offset = 5
        else:
            offset = 4
        year_group = start_of_academic_year - input_date.year - offset
        if year_group == 0:
            return "Reception"
        if year_group < 0:
            return "Student too young for school"
        if year_group > 13:
            raise InvalidYearGroupError(f"Year {year_group}")
        else:
            return f"Year {year_group}"
    except (TypeError, InvalidYearGroupError):
        if errors == "ignore":
            return None
        raise
