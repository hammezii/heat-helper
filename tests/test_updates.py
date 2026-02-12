import pytest
import pandas as pd
import numpy as np
from datetime import date
from pandas.testing import assert_series_equal

from heat_helper.updates import get_updates, get_contextual_updates
from heat_helper.exceptions import ColumnDoesNotExistError

@pytest.fixture
def sample_data():
    """Provides a basic new_df and heat_df for update functions."""
    new_df = pd.DataFrame(
        {
            "Name": ["Alice", "Bob", "Charlie", "Izzy", "Hannah"],
            "DOB": [date(2008, 1, 2), date(2008, 11, 20), date(2008, 10, 31), date(2008, 8, 16), date(2008, 12, 18)],
            "Numbers": [1, 1, 5, 4, 6],
            "Float": [1.1, 2.56, 1.34, 1.00000001, 1.6],
            "HEAT: Name": ["Alice", "Robert", "Charlie", "Isobel", "Hannah"],
            "HEAT: DOB": [date(2008, 1, 2), date(2008, 11, 2), date(2008, 10, 31), date(2008, 8, 16), date(2008, 12, 19)],
            "HEAT: Numbers": [1, 8, 5, 4, 6],
            "HEAT: Float": [1.1, 2.26, 1.34, 1.0000001, 13.6]
        }
    )
    return new_df


def test_get_updates_string(sample_data):
    new_df = sample_data
    result = get_updates(new_df, 'Name', 'HEAT: Name')
    
    # Row 0: Same -> NaN
    # Row 1: Different -> 'B'
    # Row 2: Same -> NaN
    assert pd.isna(result[0])
    assert result[1] == 'Bob'
    assert pd.isna(result[2])
    assert result[3] == 'Izzy'
    assert pd.isna(result[4])

def test_get_updates_dates(sample_data):
    new_df = sample_data
    result = get_updates(new_df, 'DOB', 'HEAT: DOB')
    
    assert pd.isna(result[0])
    assert result[1] == date(2008, 11, 20)
    assert pd.isna(result[2])
    assert pd.isna(result[3])
    assert result[4] == date(2008, 12, 18)

def test_get_updates_ints(sample_data):
    new_df = sample_data
    result = get_updates(new_df, 'Numbers', 'HEAT: Numbers')
    
    assert pd.isna(result[0])
    assert result[1] == 1
    assert pd.isna(result[2])
    assert pd.isna(result[3])
    assert pd.isna(result[4])

def test_get_updates_floats(sample_data):
    new_df = sample_data
    result = get_updates(new_df, 'Float', 'HEAT: Float')
    
    assert pd.isna(result[0])
    assert result[1] == 2.56
    assert pd.isna(result[2])
    assert result[3] == 1.00000001
    assert result[4] == 1.6

# Test null handling
def test_get_updates_null_handling():
    """Test that NaN vs NaN is treated as equal (no update)."""
    df = pd.DataFrame({
        'new': [np.nan, 'A', np.nan],
        'old': [np.nan, np.nan, 'B']
    })
    result = get_updates(df, 'new', 'old')
    
    assert pd.isna(result[0])    # NaN == NaN (no update)
    assert result[1] == 'A'      # Val vs NaN (update)
    assert pd.isna(result[2])

# Test Errors
def test_get_updates_type_errors():
    """Test the isinstance checks for inputs."""
    with pytest.raises(TypeError):
        get_updates("not a dataframe", "col1", "col2")
    
    df = pd.DataFrame({'A': [1], 'B': [1]})
    with pytest.raises(TypeError, match="Text must be a string"):
        get_updates(df, 123, "B")
    
    with pytest.raises(TypeError, match="Text must be a string"):
        get_updates(df, "A", 123)

def test_get_updates_missing_column():
    """Test that missing columns raise the custom error."""
    df = pd.DataFrame({'A': [1], 'B': [1]})
    with pytest.raises(ColumnDoesNotExistError):
        get_updates(df, 'A', 'NON_EXISTENT')
    with pytest.raises(ColumnDoesNotExistError):
        get_updates(df, 'NON_EXISTENT', 'B')

def test_get_updates_dtype_warning(capsys):
    """Checks if the warning prints when dtypes are different (e.g., int vs float)."""
    # Create data with different dtypes: 'new' is int64, 'old' is float64
    df = pd.DataFrame({
        'new': [1, 2, 3],
        'old': [1.0, 2.0, 4.0]
    })
    
    # Run the function
    get_updates(df, 'new', 'old')
    
    # Capture the printed output
    captured = capsys.readouterr()
    
    # Assert that the warning message appeared in the output
    assert "WARNING: Type Mismatch" in captured.out
    assert "int64" in captured.out
    assert "float64" in captured.out


def test_get_contextual_updates():
    """Test that NaN vs NaN is treated as equal (no update)."""
    df = pd.DataFrame({
        'new': ['Unknown', 'Yes', 'Not available', 'No', 'Yes', 'Yes'],
        'old': ['Yes', 'Yes', 'Yes', 'No', 'Yes', 'No']
    })
    bad = ['Unknown', 'Not available']
    result = get_contextual_updates(df, 'new', 'old', bad)
    
    assert pd.isna(result[0]) # Don't update as new = bad value
    assert pd.isna(result[1]) # Don't update as new = old
    assert pd.isna(result[2]) # Don't update as new = bad value
    assert pd.isna(result[3]) # Don't update as new = old
    assert pd.isna(result[4]) # Don't update as new = old
    assert result[5] == 'Yes' # Update as new data is good and they're different


def test_get_updates_type_errors_contextual():
    """Test the isinstance checks for inputs."""
    bad = ['Unknown', 'Not available']
    with pytest.raises(TypeError):
        get_contextual_updates("not a dataframe", "col1", "col2", bad)
    
    df = pd.DataFrame({'A': [1], 'B': [1]})
    with pytest.raises(TypeError, match="Text must be a string"):
        get_contextual_updates(df, 123, "B", bad)
    
    with pytest.raises(TypeError, match="Text must be a string"):
        get_contextual_updates(df, "A", 123, bad)

def test_get_updates_missing_column_contextual():
    """Test that missing columns raise the custom error."""
    df = pd.DataFrame({'A': [1], 'B': [1]})
    bad = ['Unknown', 'Not available']
    with pytest.raises(ColumnDoesNotExistError):
        get_contextual_updates(df, 'A', 'NON_EXISTENT', bad)
    with pytest.raises(ColumnDoesNotExistError):
        get_contextual_updates(df, 'NON_EXISTENT', 'B', bad)

def test_get_updates_dtype_warning_contextual(capsys):
    """Checks if the warning prints when dtypes are different (e.g., int vs float)."""
    # Create data with different dtypes: 'new' is int64, 'old' is float64
    df = pd.DataFrame({
        'new': [1, 2, 3],
        'old': [1.0, 2.0, 4.0]
    })
    bad = ['Unknown', 'Not available']
    
    # Run the function
    get_contextual_updates(df, 'new', 'old', bad)
    
    # Capture the printed output
    captured = capsys.readouterr()
    
    # Assert that the warning message appeared in the output
    assert "WARNING: Type Mismatch" in captured.out
    assert "int64" in captured.out
    assert "float64" in captured.out

def test_get_contextual_updates_bad_values_type_error():
    """Triggers TypeError for the bad_values list."""
    df = pd.DataFrame({'A': [1], 'B': [1]})
    with pytest.raises(TypeError, match="must be Iterable"):
        # Passing a string instead of a list
        get_contextual_updates(df, "A", "B", "not a list")


@pytest.fixture
def sample_df():
    """Provides a consistent DataFrame for testing."""
    return pd.DataFrame({
        "new_data": ["A", "B", "Unknown", "Not available", "C"],
        "heat_data": ["A", "X", "Y", "Z", "C"]
    })

@pytest.mark.parametrize("bad_values_input", [
    ["Unknown", "Not available"],        # List
    ("Unknown", "Not available"),        # Tuple
    {"Unknown", "Not available"},        # Set
])
def test_get_contextual_updates_iterables(sample_df, bad_values_input):
    """Tests that lists, tuples, and sets all filter 'bad' values correctly."""
    
    result = get_contextual_updates(
        df=sample_df,
        new_col="new_data",
        heat_col="heat_data",
        bad_values=bad_values_input
    )

    # Expected logic: 
    # Row 0: A == A -> No update (None)
    # Row 1: B != X -> Update with 'B'
    # Row 2: Unknown is 'bad' -> No update (None)
    # Row 3: Not available is 'bad' -> No update (None)
    # Row 4: C == C -> No update (None)
    expected = pd.Series([None, "B", None, None, None], name="new_data")
    
    assert_series_equal(result, expected)

def test_get_contextual_updates_rejects_string(sample_df):
    """Verifies that a single string raises a TypeError even though it's technically iterable."""
    with pytest.raises(TypeError, match="must be Iterable"):
        get_contextual_updates(
            df=sample_df,
            new_col="new_data",
            heat_col="heat_data",
            bad_values="Unknown" # Passing a string instead of a collection
        )