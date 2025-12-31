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
    with pytest.raises(ValueError):
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
