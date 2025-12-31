import pytest
from datetime import date
from heat_helper.yeargroup import clean_year_group, calculate_year_group_from_date
from heat_helper.exceptions import InvalidYearGroupError, FELevelError


@pytest.mark.parametrize(
    "input_val, expected",
    [
        ("Year 7", "Year 7"),
        ("y11", "Year 11"),
        ("Rec", "Reception"),
        (0, "Reception"),
        ("Year R", "Reception"),
        (13, "Year 13"),
        ("Year 07", "Year 7"),
        ("Year Group 8", "Year 8"),
        ("Y9", "Year 9"),
        ("Reception", "Reception"),
    ],
)
def test_clean_year_group_variations(input_val, expected):
    assert clean_year_group(input_val) == expected


def test_invalid_year_ranges():
    # Test lower boundary
    with pytest.raises(InvalidYearGroupError):
        clean_year_group(-1)

    # Test upper boundary
    with pytest.raises(InvalidYearGroupError):
        clean_year_group(14)


def test_clean_year_group_ignore():
    # Should return original string because 'Unknown' isn't a year
    assert clean_year_group("Unknown", errors="ignore") == "Unknown"


def test_clean_year_group_coerce():
    # Should return original string because 'Unknown' isn't a year
    assert clean_year_group("Unknown", errors="coerce") is None


def test_fe_level():
    with pytest.raises(FELevelError):
        clean_year_group("FE Level 3")


def test_level():
    with pytest.raises(FELevelError):
        clean_year_group("Level 2")


def test_calculate_year_group_branches():
    # Test Autumn birth (offset 5)
    # Born Sept 2020, Start of year 2025 -> 2025 - 2020 - 5 = 0 (Reception)
    assert calculate_year_group_from_date(date(2020, 9, 1), 2025) == "Reception"

    # Test Spring birth (offset 4)
    # Born Jan 2020, Start of year 2025 -> 2025 - 2020 - 4 = 1 (Year 1)
    assert calculate_year_group_from_date(date(2020, 1, 1), 2025) == "Year 1"

    # Test 'Too young' branch
    # Born 2024, Start of year 2025 -> 2025 - 2024 - 4 = -3
    assert (
        calculate_year_group_from_date(date(2024, 1, 1), 2025)
        == "Student too young for school"
    )


def test_calculate_year_group_errors():
    # Test TypeError raise
    with pytest.raises(TypeError):
        calculate_year_group_from_date("2020-01-01", 2025)

    # Test errors='ignore' branch
    assert calculate_year_group_from_date(123, 2025, errors="ignore") is None
