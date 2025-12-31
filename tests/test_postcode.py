import pytest
from heat_helper.postcode import format_postcode
from heat_helper.exceptions import InvalidPostcodeError
from heat_helper.core import _is_valid_postcode


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("st55bg", "ST5 5BG"),  # Lowercase, no space
        ("M1 1AA", "M1 1AA"),  # Already correct
        ("sw1a1aa", "SW1A 1AA"),  # 7-digit long format
        ("  B1 2he  ", "B1 2HE"),  # Extra whitespace
        ("ST1       1AA", "ST1 1AA"),  # Extra spaces in the middle
    ],
)
def test_postcode_cleaning(raw, expected):
    assert format_postcode(raw) == expected


def test_format_postcode_validation_success():
    # Should clean and validate correctly
    assert format_postcode("ec1a1bb") == "EC1A 1BB"


def test_format_postcode_validation_failure():
    # This matches length rules but fails the AA9 pattern
    # (Starting with 3 letters isn't a valid UK format)
    with pytest.raises(InvalidPostcodeError):
        format_postcode("ABC1 1AA")


def test_format_postcode_coerce():
    # Should return None for invalid lengths
    assert format_postcode("123", errors="coerce") is None
    assert format_postcode("ST1", errors="coerce") is None
    assert format_postcode(12, errors="coerce") is None
    assert format_postcode("NOT A POSTCODE", errors="coerce") is None


def test_format_postcode_ignore():
    # Should return None for invalid lengths
    assert format_postcode("12345", errors="ignore") == "12345"
    assert format_postcode("ST1", errors="ignore") == "ST1"
    assert format_postcode(12, errors="ignore") == 12


def test_postcode_type_safety():
    # Testing that it catches non-string inputs
    with pytest.raises(TypeError):
        format_postcode(12345)

    # Testing ignore mode for a number
    assert format_postcode(12345, errors="ignore") == 12345


# POSTCODE CHECK
@pytest.mark.parametrize(
    "postcode, expected",
    [
        ("CR2 6XH", True),  # AA9 9AA
        ("DN55 1PT", True),  # AA99 9AA
        ("M1 1AE", True),  # A9 9AA
        ("B33 8TH", True),  # A99 9AA
        ("W1A 0AX", True),  # A9A 9AA
        ("EC1A 1BB", True),  # AA9A 9AA
        ("12 345", False),  # Numbers first
        ("ABC 123", False),  # Too many letters in outward
        ("SW1A 1A", False),  # Inward too short
        ("", False),  # Empty string
        (None, False),  # Non-string input
    ],
)
def test_is_valid_postcode_logic(postcode, expected):
    assert _is_valid_postcode(postcode) == expected