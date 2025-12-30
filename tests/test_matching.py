import pytest
import pandas as pd
import numpy as np
from heat_helper.matching import perform_exact_match, perform_fuzzy_match
from heat_helper.exceptions import ColumnDoesNotExistError, FilterColumnMismatchError, FuzzyMatchIndexError

@pytest.fixture
def sample_data():
    """Provides a basic new_df and heat_df for matching."""
    new_df = pd.DataFrame({
        "ID": [1, 2, 3],
        "Name": ["Alice", "Bob", "Charlie"],
        "DOB": ["2010-01-01", "2010-02-02", "2010-03-03"]
    })
    heat_df = pd.DataFrame({
        "Student HEAT ID": ["H1", "H2"],
        "Full Name": ["Alice", "Bob"],
        "Birth Date": ["2010-01-01", "2010-02-02"],
        "Postcode": ["ST1", "ST2"]
    })
    return new_df, heat_df

# --- SUCCESS PATHS ---

def test_perform_exact_match_success(sample_data):
    new_df, heat_df = sample_data
    matched, unmatched = perform_exact_match(
        unmatched_df=new_df,
        heat_df=heat_df,
        left_join_cols=["Name", "DOB"],
        right_join_cols=["Full Name", "Birth Date"],
        match_type_desc="Exact Name and DOB"
    )
    
    # Alice and Bob should match, Charlie should not
    assert len(matched) == 2
    assert len(unmatched) == 1
    assert "Student HEAT ID" in matched.columns
    assert matched.iloc[0]["Match Type"] == "Exact Name and DOB"
    assert unmatched.iloc[0]["Name"] == "Charlie"

def test_perform_exact_match_verify_flag(sample_data):
    new_df, heat_df = sample_data
    # Testing the 'verify=True' branch which re-joins all HEAT columns
    matched, _ = perform_exact_match(
        new_df, heat_df, ["Name"], ["Full Name"], 
        "Verify Match", verify=True
    )
    
    # Should contain original HEAT columns prefixed with 'HEAT: '
    assert "HEAT: Postcode" in matched.columns
    assert matched.iloc[0]["HEAT: Postcode"] == "ST1"

def test_perform_exact_match_duplicates(sample_data, capsys):
    new_df, heat_df = sample_data
    # Create a duplicate in HEAT to trigger the WARNING print statement
    heat_df_dupe = pd.concat([heat_df, pd.DataFrame({
        "Student HEAT ID": ["H1_DUPE"], 
        "Full Name": ["Alice"], 
        "Birth Date": ["2010-01-01"]
    })], ignore_index=True)
    
    matched, _ = perform_exact_match(
        new_df, heat_df_dupe, ["Name"], ["Full Name"], "Dupe Test"
    )
    
    captured = capsys.readouterr()
    assert "WARNING" in captured.out
    assert "extra record(s) created" in captured.out

# --- ERROR HANDLING & BRANCHES ---

def test_perform_exact_match_type_error():
    with pytest.raises(TypeError, match="must be pandas DataFrames"):
        perform_exact_match([], pd.DataFrame(), [], [], "test")

def test_perform_exact_match_missing_cols(sample_data):
    new_df, heat_df = sample_data
    
    # Missing in new_df
    with pytest.raises(ColumnDoesNotExistError, match="not found in new_df"):
        perform_exact_match(new_df, heat_df, ["WrongCol"], ["Full Name"], "test")
        
    # Missing in heat_df
    with pytest.raises(ColumnDoesNotExistError, match="not found in heat_df"):
        perform_exact_match(new_df, heat_df, ["Name"], ["WrongCol"], "test")

def test_perform_exact_match_custom_id_col(sample_data):
    new_df, heat_df = sample_data
    heat_df = heat_df.rename(columns={"Student HEAT ID": "Legacy ID"})
    
    # Test custom ID column name
    matched, _ = perform_exact_match(
        new_df, heat_df, ["Name"], ["Full Name"], "Custom ID",
        student_heat_id_col="Legacy ID"
    )
    assert "Legacy ID" in matched.columns

def test_perform_exact_match_missing_id_col(sample_data):
    new_df, heat_df = sample_data
    with pytest.raises(ColumnDoesNotExistError, match="ID column 'Wrong ID' not found"):
        perform_exact_match(new_df, heat_df, ["Name"], ["Full Name"], "test", student_heat_id_col="Wrong ID")


# FUZZY MATCHING TESTS

@pytest.fixture
def sample_heat():
    return pd.DataFrame({
        "ID": [1, 2],
        "Name": ["John Smith", "Jane Doe"],
        "DOB": ["2000-01-01", "1995-05-05"],
        "Postcode": ["A1 1AA", "B2 2BB"]
    })

@pytest.fixture
def sample_unmatched():
    return pd.DataFrame({
        "External_Name": ["Jon Smith", "Alex Vane"],
        "Birth_Date": ["2000-01-01", "1990-10-10"],
        "PC": ["A1 1AA", "C3 3CC"]
    })

# --- Tests ---

def test_successful_fuzzy_match(sample_unmatched, sample_heat):
    """Test a successful match with renaming and filtering."""
    matches, remaining = perform_fuzzy_match(
        unmatched_df=sample_unmatched,
        heat_df=sample_heat,
        left_filter_cols=["Birth_Date", "PC"],
        right_filter_cols=["DOB", "Postcode"],
        left_name_col="External_Name",
        right_name_col="Name",
        match_desc="DOB+PC Match",
        threshold=80
    )
    
    # Assertions
    assert len(matches) == 1
    assert len(remaining) == 1
    assert matches.iloc[0]["HEAT: Name"] == "John Smith"
    assert matches.iloc[0]["Match Type"] == "DOB+PC Match"
    assert "Fuzzy Score" in matches.columns
    # Check if suffix was removed and prefix added
    assert "HEAT: ID" in matches.columns

def test_no_matches_found(sample_unmatched, sample_heat):
    """Test behavior when threshold is too high for any matches."""
    matches, remaining = perform_fuzzy_match(
        unmatched_df=sample_unmatched,
        heat_df=sample_heat,
        left_filter_cols=["Birth_Date"],
        right_filter_cols=["DOB"],
        left_name_col="External_Name",
        right_name_col="Name",
        match_desc="Strict Match",
        threshold=100 # Impossible match for 'Jon' vs 'John'
    )
    assert matches.empty
    assert len(remaining) == 2

def test_type_error_input():
    with pytest.raises(TypeError, match="must be pandas DataFrames"):
        perform_fuzzy_match([], pd.DataFrame(), [], [], "", "", "")

def test_column_existence_errors(sample_unmatched, sample_heat):
    # Test missing left filter col
    with pytest.raises(ColumnDoesNotExistError, match="'Missing' not found in unmatched_df"):
        perform_fuzzy_match(sample_unmatched, sample_heat, ["Missing"], ["DOB"], "External_Name", "Name", "T")
    
    # Test missing right filter col
    with pytest.raises(ColumnDoesNotExistError, match="'Missing' not found in heat_df"):
        perform_fuzzy_match(sample_unmatched, sample_heat, ["Birth_Date"], ["Missing"], "External_Name", "Name", "T")

def test_filter_mismatch_error(sample_unmatched, sample_heat):
    with pytest.raises(FilterColumnMismatchError):
        perform_fuzzy_match(sample_unmatched, sample_heat, ["Birth_Date"], ["DOB", "Postcode"], "External_Name", "Name", "T")

def test_non_unique_index_error(sample_heat):
    df_non_unique = pd.DataFrame({"Name": ["A", "B"]}, index=[0, 0])
    with pytest.raises(FuzzyMatchIndexError):
        perform_fuzzy_match(df_non_unique, sample_heat, [], [], "Name", "Name", "T")

def test_column_collision_warning(sample_unmatched, sample_heat, capsys):
    # Add a column that triggers the warning
    sample_unmatched["Old_Score_HEAT"] = 90
    perform_fuzzy_match(
        sample_unmatched, sample_heat, ["Birth_Date"], ["DOB"], "External_Name", "Name", "T"
    )
    captured = capsys.readouterr()
    assert "WARNING" in captured.out

def test_nan_handling_in_keys(sample_heat):
    """Ensures that rows with NaNs in filter columns don't crash the grouper."""
    unmatched_nan = pd.DataFrame({
        "Name": ["John"],
        "DOB": [np.nan]
    })
    heat_nan = pd.DataFrame({
        "Name": ["John"],
        "DOB": [np.nan]
    })
    
    matches, _ = perform_fuzzy_match(
        unmatched_nan, heat_nan, ["DOB"], ["DOB"], "Name", "Name", "T"
    )
    # Depending on how pandas groups NaNs, this might be 0 or 1. 
    # Current code handles it by tuple(row) which includes np.nan.
    assert isinstance(matches, pd.DataFrame)