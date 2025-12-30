import pytest
from heat_helper.yeargroup import clean_year_group
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
