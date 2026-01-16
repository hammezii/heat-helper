# Import internal libraries
from datetime import date

# Import external libraries
import pandas as pd

# Import helper functions
from heat_helper.core import _parse_year_group_to_int, CURRENT_ACADEMIC_YEAR_START
from heat_helper.exceptions import InvalidYearGroupError, FELevelError


def reverse_date(input_date: date, errors: str = "raise") -> date:
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
            raise TypeError(
                f"input_date must be date format, not {type(input_date).__name__}"
            )
        if input_date.day > 12:
            return input_date
        else:
            return input_date.replace(day=input_date.month, month=input_date.day)
    except (TypeError, NameError):
        if errors == "ignore":
            return input_date
        raise


def calculate_dob_range_from_year_group(
    year_group: str | int | pd.Series,
    start_year: int = CURRENT_ACADEMIC_YEAR_START,
    errors: str = "raise",
) -> tuple[date | None, date | None] | tuple[pd.Series, pd.Series]:
    """Calculates the expected DOB range (Sep 1 to Aug 31) for a given year group (1 to 13) in England.
    Includes some logic to try to handle Reception if entered as 'Reception', 'R', or 'Year R'.

    Args:
        year_group: The year group you want to find the date of birth range for. Examples: 'Year 10', 'Y10', 10. Note: Reception should be entered as Reception, Year R or R.
        start_year (optional): The year in which the academic year starts for the academic year you want to calculate. Example: for 2025/2026 enter 2025. You can enter any year here and it will return the date of birth range for someone in that year group during the specified academic year. Default is start of current academic year.
        errors (optional): default = 'raise' which raises all errors. 'ignore' and 'coerce' returns None, None.

    Raises:
        InvalidYearGroupError: Raised when `year_group` input cannot be parsed or is out of range.
        SchoolYearError: Raised when `start_year` is not a valid int.
        FELevelError: Raised if FE Levels are in `year_group`.

    Returns:
        The date of birth range. First date is start of the academic year; second date is the end of the academic year. Example: 01/09/2013, 31/08/2014."""
    
    try:
        # Dataframe
        if isinstance(year_group, pd.Series):
            results = year_group.apply(
                calculate_dob_range_from_year_group, 
                start_year=start_year, 
                errors=errors
            )
            
            start_dates, end_dates = zip(*results)
            return (pd.Series(start_dates, index=year_group.index), 
                    pd.Series(end_dates, index=year_group.index))

        # Individual values
        y_num = _parse_year_group_to_int(year_group)
        dob_start_year = int(start_year) - (y_num + 5)
        return date(dob_start_year, 9, 1), date(dob_start_year + 1, 8, 31)
    except (InvalidYearGroupError, TypeError, ValueError, FELevelError):
        if errors == "coerce":
            return None, None
        if errors == "ignore":
            return None, None  # Dates usually can't be 'ignored' as strings
        raise
