import pytest
import pandas as pd
from heat_helper.names import (
    format_name,
    find_numbers_in_text,
    remove_numbers_from_text,
    remove_diacritics,
    create_full_name,
)


# --- FORMAT NAMES TESTS ---
@pytest.mark.parametrize(
    "name, clean_name",
    [
        ("JANE DOE", "Jane Doe"),
        ("jane DOE", "Jane Doe"),
        ("Jane - Jane Doe", "Jane-Jane Doe"),
        ("Jane- Jane Doe", "Jane-Jane Doe"),
        ("Jane O'Doe", "Jane O'Doe"),
        ("Jane McDoe", "Jane McDoe"),
        ("Jane    Doe", "Jane Doe"),
        ("Jane Doe ", "Jane Doe"),
        (" Jane   Doe ", "Jane Doe"),
        ("mcdonald", "McDonald"),
        ("o'reilly", "O'Reilly"),
        ("o'connor-mcdonald", "O'Connor-McDonald"),
    ],
)
def test_format_names(name, clean_name):
    assert format_name(name) == clean_name


def test_format_names_not_str_raises_error():
    text = 12
    with pytest.raises(
        TypeError, match=f"Text must be a string, not {type(text).__name__}"
    ):
        format_name(text)


def test_format_name_ignore_errors():
    assert format_name(12, errors="ignore") == 12


def test_format_name_coerce_errors():
    assert format_name(12, errors="coerce") == None


# FIND NUMBERS IN TEXT
@pytest.mark.parametrize(
    "num_name, clean_num_name",
    [
        ("Jane Doe", False),
        ("Jane O'Doe", False),
        ("Jane Doe 21", True),
        ("1 Jane Doe 79", True),
        ("J4ne", True),
    ],
)
def test_find_numbers(num_name, clean_num_name):
    assert find_numbers_in_text(num_name) == clean_num_name


def test_find_numbers_error():
    with pytest.raises(
        TypeError, match=f"Text must be a string, not {type(12).__name__}"
    ):
        find_numbers_in_text(12)


def test_find_numbers_convert():
    assert find_numbers_in_text(12, convert_to_string=True) == True


def test_find_numbers_ignore():
    assert (
        find_numbers_in_text(123, errors="ignore")
        == "Input not string: result unknown."
    )


def test_find_numbers_coerce():
    # Should convert 123 to "123" and then return True
    assert find_numbers_in_text(123, errors="coerce") == None


# REMOVE NUMBERS
def test_remove_numbers_error():
    with pytest.raises(
        TypeError, match=f"Text must be a string, not {type(12).__name__}"
    ):
        remove_numbers_from_text(12)


def test_remove_numbers_convert():
    assert remove_numbers_from_text(12, convert_to_string=True) == ""


def test_remove_numbers_ignore_errors():
    assert (
        remove_numbers_from_text(12, errors="ignore")
        == "Input not string: can't remove numbers."
    )


@pytest.mark.parametrize(
    "num_name, remove_num_name",
    [
        ("Jane Doe", "Jane Doe"),
        ("Jane Doe 21", "Jane Doe"),
        ("1 Jane Doe 79", "Jane Doe"),
        ("  23 Jane", "Jane"),
    ],
)
def test_remove_numbers(num_name, remove_num_name):
    assert remove_numbers_from_text(num_name) == remove_num_name


def test_remove_numbers_coerce():
    # Trigger the 'coerce' block in the except TypeError clause
    assert remove_numbers_from_text(123, errors="coerce") == None


# DIACRITICS
def test_basic_diacritics():
    """Test standard European accents."""
    assert remove_diacritics("Crème brûlée") == "Creme brulee"
    assert remove_diacritics("Zoë") == "Zoe"
    assert remove_diacritics("Muñoz") == "Munoz"


def test_no_diacritics():
    """Test string that already has no accents."""
    assert remove_diacritics("London") == "London"


def test_empty_string():
    """Test handling of empty strings."""
    assert remove_diacritics("") == ""


def test_compatibility_characters():
    """Test NFKD decomposition of formatting (e.g., superscripts)."""
    # NFKD turns ² into 2
    assert remove_diacritics("Area²") == "Area2"


def test_type_error_raised():
    """Verify TypeError is raised for non-string input by default."""
    with pytest.raises(TypeError, match="Input must be a string"):
        remove_diacritics(123)


def test_errors_ignore():
    """Verify original input is returned when errors='ignore'."""
    assert remove_diacritics(123, errors="ignore") == 123
    assert remove_diacritics(None, errors="ignore") is None


def test_errors_coerce():
    """Verify input is cast to string when errors='coerce'."""
    assert remove_diacritics(123, errors="coerce") == None
    assert remove_diacritics(True, errors="coerce") == None


# CREATE FULL NAME
def test_create_full_name_strings():
    # Test basic string concatenation
    assert create_full_name("Jane", "Doe", "Middle") == "Jane Middle Doe"
    # Test handling of empty middle name
    assert create_full_name("Jane", "Doe") == "Jane Doe"
    # Test extra spacing handling
    assert create_full_name(" Jane ", " Doe", "  ") == "Jane Doe"


def test_create_full_name_pandas():
    # Test pandas Series logic
    fnames = pd.Series(["Jane", "John"])
    lnames = pd.Series(["Doe", "Smith"])
    result = create_full_name(fnames, lnames)

    expected = pd.Series(["Jane Doe", "John Smith"])
    pd.testing.assert_series_equal(result, expected)
