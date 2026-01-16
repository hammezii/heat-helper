import pytest
import pandas as pd
from heat_helper.names import (
    format_name,
    find_numbers_in_text,
    remove_numbers,
    remove_diacritics,
    create_full_name,
    remove_punctuation
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
        == 123
    )


def test_find_numbers_coerce():
    # Should convert 123 to "123" and then return True
    assert find_numbers_in_text(123, errors="coerce") == None


# REMOVE NUMBERS
def test_remove_numbers_error():
    with pytest.raises(
        TypeError, match=f"Text must be a string, not {type(12).__name__}"
    ):
        remove_numbers(12)


def test_remove_numbers_convert():
    assert remove_numbers(12, convert_to_string=True) == ""


def test_remove_numbers_ignore_errors():
    assert (
        remove_numbers(12, errors="ignore")
        == 12
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
    assert remove_numbers(num_name) == remove_num_name


def test_remove_numbers_coerce():
    # Trigger the 'coerce' block in the except TypeError clause
    assert remove_numbers(123, errors="coerce") == None


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


# Test Remove punctuation
def test_punctuation_replacement_with_space():
    """
    Verifies that punctuation is replaced by a space, 
    preventing words from merging.
    """
    # "word...word" -> "word   word" -> "word word"
    assert remove_punctuation("word...word") == "word word"

def test_standard_cleaning():
    """Checks a mix of different punctuation marks and spacing."""
    input_text = "hello! [world]? this... is ; a test."
    expected = "hello world this is a test"
    assert remove_punctuation(input_text) == expected

def test_whitespace_collapsing():
    """Ensures that multiple spaces (original or created) are reduced to one."""
    input_text = "space      between , and , dots..."
    # Should not result in "space between   and   dots "
    assert remove_punctuation(input_text) == "space between and dots"

def test_numeric_strings():
    """Checks that numbers remain intact but separators are removed."""
    assert remove_punctuation("123,456!") == "123 456"

@pytest.mark.parametrize("input_val, error_mode, expected", [
    (None, "coerce", None),
    (100, "ignore", 100),
    ([], "coerce", None),
])
def test_error_handling_modes(input_val, error_mode, expected):
    """Tests the 'coerce' and 'ignore' safety valves for non-string types."""
    assert remove_punctuation(input_val, errors=error_mode) == expected

def test_raise_on_invalid_type():
    """Ensures the function raises TypeError by default for non-strings."""
    with pytest.raises(TypeError, match="Input must be a string"):
        remove_punctuation({"key": "value"})

def test_custom_punctuation_override():
    """Ensures the function respects the 'punctuation' argument if provided."""
    # Only remove the '@', leave the '!'
    assert remove_punctuation("user@host!", punctuation="@") == "user host!"