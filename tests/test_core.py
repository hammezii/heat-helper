import pytest
from datetime import date
from heat_helper.core import (
    _calc_current_academic_year_start,
    _parse_year_group_to_int
)



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


def test_parse_year_group_error():
    with pytest.raises(TypeError, match="str or int"): # Matches your current code typo
        _parse_year_group_to_int(6.245)