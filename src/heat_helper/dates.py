#Import internal libraries
from datetime import date

#Import external libraries
import pandas as pd

#Import helper functions
from .core import _parse_year_group_to_int
from .exceptions import InvalidYearGroupError


def reverse_date(input_date: date, errors: str = 'raise') -> date:
    """Sometimes dates are incorrectly formatted by Excel such that the day and month is swapped around. This can create errors when reading the data into pandas DataFrames. This function can be used to create a 'reversed' date where the day and month are swapped around. If this creates a date which doesn't exist, the original date is returned.

    Args:
        input_date: The date you wish to 'reverse' (swap day and month).
        errors: Defaults to 'raise' which raises errors. 'ignore' ignores errors and returns original date.

    Raises:
        TypeError: Raised if input_date is not in the date format (or pandas datetime format.)

    Returns:
        date: Reversed date or original date if reversed date does not exist.
    """
    try:
        if pd.isna(input_date):
            return input_date
        if not isinstance(input_date, date):
            raise TypeError(f"Input must be date format, not {type(input_date).__name__}")
        if input_date.day > 12:
            return input_date
        else:
            return input_date.replace(day=input_date.month, month=input_date.day)
    except(TypeError, NameError):
        if errors == "ignore":
            return input_date
        raise


def calculate_year_group_from_date(input_date: date, start_of_academic_year: int, errors: str = 'raise') -> str | None:
    """Calculates school year group from date of birth for the English school system. Returns 'Year i' or 'Reception', or 'Student too young for school' if date of birth is not of school age.

    Args:
        input_date (date): Date of birth you wish to know the school year for.
        start_of_academic_year (int): The school year in which you want to calculate the year group for. Allows you to calculate a year group for any academic year not just current e.g. for 2025/26 school year enter 2025.

    Raises:
        TypeError: Raised if input_date is not a date.

    Returns:
        Returns 'Year i' or 'Reception' or 'Student too young for school'.
    """
    try:
        if not isinstance(input_date, date):
            raise TypeError(f"Input must be a date, not {type(input_date).__name__}")
        if input_date.month in [9, 10, 11]:
            offset = 5
        else:
            offset = 4
        year_group = start_of_academic_year - input_date.year - offset
        if year_group == 0:
            return "Reception"
        elif year_group < 0:
            return "Student too young for school"
        else:
            return f"Year {year_group}"
    except:
        if errors == 'ignore':
            return None
        raise


def calculate_dob_range_from_year_group(
    year_group: str | int, start_year: int, errors: str = "raise"
) -> tuple[date | None, date | None]:
    """Calculates the expected DOB range (Sep 1 to Aug 31) for a given year group (1 to 13) in England.
    Include some logic to try to handle Reception if entered as 'Reception', 'R', or 'Year R'.

    Args:
        year_group: The year group you want to find the date of birth range for. Examples: 'Year 10', 'Y10', 10. Note: Reception should be entered as Reception, Year R or R.
        start_year: The year in which the academic year starts for the academic year you want to calculate. Example: for 2025/2026 enter 2025. You can enter any year here and it will return the date of birth range for someone in that year group during the specified academic year.
        errors (optional): default = 'raise' which raises all errors. 'ignore' returns orignal value, 'coerce' returns None.

    Raises:
        InvalidYearGroupError: Raised when the year group input cannot be parsed or is out of range.
        SchoolYearError: Raised when start_year is not a valid int.

    Returns:
        The date of birth range. First date is start of the academic year; second date is the end of the academic year. Example: 01/09/2013, 31/08/2014."""
    try:
        y_num = _parse_year_group_to_int(year_group)
        dob_start_year = int(start_year) - (y_num + 5)
        return date(dob_start_year, 9, 1), date(dob_start_year + 1, 8, 31)
    except (InvalidYearGroupError, TypeError, ValueError):
        if errors == "ignore":
            return None, None  # Dates usually can't be 'ignored' as strings
        if errors == "coerce":
            return None, None
        raise