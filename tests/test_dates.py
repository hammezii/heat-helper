import pytest
from datetime import date
from heat_helper.dates import (
    calculate_dob_range_from_year_group,
    reverse_date,
)
from heat_helper.exceptions import InvalidYearGroupError
import pandas as pd


# DOB Range from YG Tests
def test_dob_maths():
    # Year 7 in 2025/26 should be born Sep 2013 - Aug 2014
    start, end = calculate_dob_range_from_year_group(7, 2025)
    assert start == date(2013, 9, 1)
    assert end == date(2014, 8, 31)


def test_reception_dob_calculation():
    # Reception in 2024 (4-5 years old)
    start, _ = calculate_dob_range_from_year_group("R", 2024)
    assert start.year == 2019  # 2024 - (0 + 5)


def test_dob_invalidyeargrouperror():
    with pytest.raises(InvalidYearGroupError):
        calculate_dob_range_from_year_group(15, 2025)


def test_dob_errors_ignore():
    start, end = calculate_dob_range_from_year_group(15, 2025, errors="ignore")
    assert start == None
    assert end == None


def test_dob_errors_coerce():
    start, end = calculate_dob_range_from_year_group(15, errors="coerce")
    assert start == None
    assert end == None


def test_dob_range_invalid_start_year():
    # Triggers ValueError/TypeError during int(start_year) conversion
    with pytest.raises(TypeError):
        calculate_dob_range_from_year_group(7, "not_a_year")


def test_dob_range_coerce_invalid_start_year():
    # Triggers the 'coerce' return for an invalid start year
    start, end = calculate_dob_range_from_year_group(7, start_year="invalid", errors="coerce")
    assert start is None and end is None


# Reverse Date Tests
def test_reverse_date():
    assert reverse_date(date(2025, 1, 2)) == date(2025, 2, 1)


def test_no_reverse_date():
    assert reverse_date(date(2025, 2, 25)) == date(2025, 2, 25)


def test_reverse_date_pandas_na():
    # Covers the 'if pd.isna(input_date)' branch
    assert reverse_date(pd.NA) is pd.NA
    assert reverse_date(None) is None


def test_reverse_date_type_error():
    # Covers the raise TypeError branch
    with pytest.raises(TypeError, match="input_date must be date format"):
        reverse_date("2025-01-01")


def test_reverse_date_ignore_errors():
    # Covers the 'except... if errors == "ignore"' branch
    assert reverse_date("not a date", errors="ignore") == "not a date"

def test_calculate_dob_range_series_input():
    """
    Tests that passing a pd.Series returns two pd.Series with correct 
    date values and matching indices.
    """
    # 1. Setup: Create a Series with a mix of valid inputs
    # Using start_year=2025 for predictable math
    year_series = pd.Series(["Year 1", "Y2", 3], index=["student_a", "student_b", "student_c"])
    test_start_year = 2025
    
    # 2. Execute: Call the function
    # Expected DOB starts: 2025 - (Y + 5)
    # Y1 -> 2019, Y2 -> 2018, Y3 -> 2017
    start_series, end_series = calculate_dob_range_from_year_group(
        year_group=year_series, 
        start_year=test_start_year
    )
    
    # 3. Assertions
    # Check types
    assert isinstance(start_series, pd.Series)
    assert isinstance(end_series, pd.Series)
    
    # Check Index preservation
    pd.testing.assert_index_equal(start_series.index, year_series.index)
    pd.testing.assert_index_equal(end_series.index, year_series.index)
    
    # Check specific values
    # For Year 1 (student_a) in 2025: DOB range should be 2019-09-01 to 2020-08-31
    assert start_series["student_a"] == date(2019, 9, 1)
    assert end_series["student_a"] == date(2020, 8, 31)
    
    # For Year 3 (student_c) in 2025: DOB range should be 2017-09-01 to 2018-08-31
    assert start_series["student_c"] == date(2017, 9, 1)
    assert end_series["student_c"] == date(2018, 8, 31)

def test_calculate_dob_range_series_with_errors_coerce():
    """
    Tests that the 'coerce' logic works when applied to a Series containing invalid data.
    """
    # Series with one valid and one invalid year group
    invalid_series = pd.Series(["Year 1", "Invalid_Year"], index=[0, 1])
    
    # Should not raise error because of errors="coerce"
    starts, ends = calculate_dob_range_from_year_group(
        invalid_series, 
        start_year=2025, 
        errors="coerce"
    )
    
    # First record should be valid
    assert starts[0] == date(2019, 9, 1)
    # Second record should be (None, None) flattened into the Series
    assert starts[1] is None
    assert ends[1] is None