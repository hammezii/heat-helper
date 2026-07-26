import pytest
import pandas as pd
from datetime import date
from pandas.testing import assert_series_equal
from heat_helper.core import (
    _calc_current_academic_year_start,
    _parse_year_group_to_int
)
from heat_helper.exceptions import InvalidYearGroupError


@pytest.mark.parametrize(
    "input_date, expected_year",
    [
        # Testing the Autumn/Winter threshold (Current year)
        (date(2024, 9, 1), 2024),
        (date(2024, 12, 31), 2024),
        # Testing the Spring/Summer threshold (Previous year)
        (date(2025, 1, 1), 2024),
        (date(2025, 8, 31), 2024),
        # Leap year check
        (date(2024, 2, 29), 2023),
        # Far future check
        (date(2030, 10, 15), 2030),
    ],
)

def test_calc_current_academic_year_start(input_date, expected_year):
    """Checks that the academic year resets correctly every September."""
    assert _calc_current_academic_year_start(input_date) == expected_year

@pytest.mark.parametrize(
    "year_group_in, year_group_out",
    [
        ('Year 10', 10),
        ('10', 10),
        (10.0, 10),
        ('Y11', 11),
        ('Reception', 0)
    ],
)

def test_parse_year_group_general(year_group_in, year_group_out):
    """Checks that year groups are returns as ex[ected]."""
    assert _parse_year_group_to_int(year_group_in) == year_group_out

def test_parse_year_group_error():
    with pytest.raises(InvalidYearGroupError, match="Invalid year group"): # Matches your current code typo
        _parse_year_group_to_int(6.245)

def test_parse_year_group_error_number_not_in_range():
    with pytest.raises(InvalidYearGroupError, match="Invalid year group"): # Matches your current code typo
        _parse_year_group_to_int(16)

def test_parse_year_group__bool_error():
    with pytest.raises(TypeError, match="Input must be str or int"): # Matches your current code typo
        _parse_year_group_to_int(True)

def test_parse_year_group_to_int_with_series():
    # Arrange: Create a series with mixed valid inputs
    input_series = pd.Series(["Year 7", 10, "reception", "  12  "])
    expected_output = pd.Series([7, 10, 0, 12])
    
    # Act: Call the function
    result = _parse_year_group_to_int(input_series)
    
    # Assert: Check if the result is a series and matches expectations
    assert isinstance(result, pd.Series)
    assert_series_equal(result, expected_output, check_dtype=False)

def test_parse_year_group_to_int_series_error_propagation():
    # Verify that errors inside the series are still raised
    input_series = pd.Series(["Year 7", "InvalidInput"])
    
    with pytest.raises(InvalidYearGroupError):
        _parse_year_group_to_int(input_series)