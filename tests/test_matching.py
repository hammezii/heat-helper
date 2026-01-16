import pytest
import pandas as pd
import numpy as np
from datetime import date
from unittest.mock import patch
from heat_helper.matching import (
    perform_exact_match,
    perform_fuzzy_match,
    perform_school_age_range_fuzzy_match,
)
from heat_helper.exceptions import (
    ColumnDoesNotExistError,
    FilterColumnMismatchError,
    FuzzyMatchIndexError,
)


@pytest.fixture
def sample_data():
    """Provides a basic new_df and heat_df for matching."""
    new_df = pd.DataFrame(
        {
            "ID": [1, 2, 3],
            "Name": ["Alice", "Bob", "Charlie"],
            "DOB": ["2010-01-01", "2010-02-02", "2010-03-03"],
        }
    )
    heat_df = pd.DataFrame(
        {
            "Student HEAT ID": ["H1", "H2"],
            "Full Name": ["Alice", "Bob"],
            "Birth Date": ["2010-01-01", "2010-02-02"],
            "Postcode": ["ST1", "ST2"],
        }
    )
    return new_df, heat_df


# --- SUCCESS PATHS ---


def test_perform_exact_match_success(sample_data):
    new_df, heat_df = sample_data
    matched, unmatched = perform_exact_match(
        unmatched_df=new_df,
        heat_df=heat_df,
        left_join_cols=["Name", "DOB"],
        right_join_cols=["Full Name", "Birth Date"],
        match_desc="Exact Name and DOB",
    )

    # Alice and Bob should match, Charlie should not
    assert len(matched) == 2
    assert len(unmatched) == 1
    assert "HEAT: Student HEAT ID" in matched.columns
    assert matched.iloc[0]["Match Type"] == "Exact Name and DOB"
    assert unmatched.iloc[0]["Name"] == "Charlie"


def test_perform_exact_match_verify_flag(sample_data):
    new_df, heat_df = sample_data
    # Testing the 'verify=True' branch which re-joins all HEAT columns
    matched, _ = perform_exact_match(
        new_df, heat_df, ["Name"], ["Full Name"], "Verify Match", verify=True
    )

    # Should contain original HEAT columns prefixed with 'HEAT: '
    assert "HEAT: Postcode" in matched.columns
    assert matched.iloc[0]["HEAT: Postcode"] == "ST1"


def test_perform_exact_match_duplicates(sample_data, capsys):
    new_df, heat_df = sample_data
    # Create a duplicate in HEAT to trigger the WARNING print statement
    heat_df_dupe = pd.concat(
        [
            heat_df,
            pd.DataFrame(
                {
                    "Student HEAT ID": ["H1_DUPE"],
                    "Full Name": ["Alice"],
                    "Birth Date": ["2010-01-01"],
                }
            ),
        ],
        ignore_index=True,
    )

    matched, _ = perform_exact_match(
        new_df, heat_df_dupe, ["Name"], ["Full Name"], "Dupe Test"
    )

    captured = capsys.readouterr()
    assert "WARNING" in captured.out
    assert "extra record(s) created" in captured.out


# --- ERROR HANDLING & BRANCHES ---

def test_perform_exact_match_empty_unmatched_df(capsys):
    """Tests the early exit clause when there are no students left to match."""
    
    # Setup: Empty unmatched_df with expected columns
    unmatched_df = pd.DataFrame(columns=["First Name", "Last Name"])
    
    # heat_df can have data, but it won't be used
    heat_df = pd.DataFrame({
        "First Name": ["John"],
        "Last Name": ["Doe"],
        "Student HEAT ID": [12345]
    })
    
    left_cols = ["First Name", "Last Name"]
    right_cols = ["First Name", "Last Name"]
    match_desc = "Name Match"

    # Execute
    matched, unmatched = perform_exact_match(
        unmatched_df, 
        heat_df, 
        left_cols, 
        right_cols, 
        match_desc
    )

    # 1. Check Return Values
    assert matched.empty
    assert unmatched.empty
    assert isinstance(matched, pd.DataFrame)
    assert isinstance(unmatched, pd.DataFrame)

    # 2. Check printed warning (using capsys fixture)
    captured = capsys.readouterr()
    expected_warning = f"WARNING: skipping match type: {match_desc} - no students left to match."
    assert expected_warning in captured.out

def test_perform_exact_match_empty_unmatched_df_preserves_columns(capsys):
    """Verifies that the returned unmatched_df retains its column structure even if empty."""
    
    unmatched_df = pd.DataFrame(columns=["Name", "DOB"])
    heat_df = pd.DataFrame({"Name": ["A"], "DOB": ["B"], "Student HEAT ID": [1]})
    
    _, unmatched = perform_exact_match(
        unmatched_df, heat_df, ["Name"], ["Name"], "Test"
    )
    
    # Ensure it didn't just return 'pd.DataFrame()' but the actual empty input df
    assert list(unmatched.columns) == ["Name", "DOB"]

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
        new_df,
        heat_df,
        ["Name"],
        ["Full Name"],
        "Custom ID",
        heat_id_col="Legacy ID",
    )
    assert "HEAT: Legacy ID" in matched.columns


def test_perform_exact_match_missing_id_col(sample_data):
    new_df, heat_df = sample_data
    with pytest.raises(ColumnDoesNotExistError, match="ID column 'Wrong ID' not found"):
        perform_exact_match(
            new_df,
            heat_df,
            ["Name"],
            ["Full Name"],
            "test",
            heat_id_col="Wrong ID",
        )


# FUZZY MATCHING TESTS


@pytest.fixture
def sample_heat():
    return pd.DataFrame(
        {
            "ID": [1, 2],
            "Name": ["John Smith", "Jane Doe"],
            "DOB": ["2000-01-01", "1995-05-05"],
            "Postcode": ["A1 1AA", "B2 2BB"],
        }
    )


@pytest.fixture
def sample_unmatched():
    return pd.DataFrame(
        {
            "External_Name": ["Jon Smith", "Alex Vane"],
            "Birth_Date": ["2000-01-01", "1990-10-10"],
            "PC": ["A1 1AA", "C3 3CC"],
        }
    )


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
        threshold=80,
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
        threshold=100,  # Impossible match for 'Jon' vs 'John'
    )
    assert matches.empty
    assert len(remaining) == 2


def test_type_error_input():
    with pytest.raises(TypeError, match="must be pandas DataFrames"):
        perform_fuzzy_match([], pd.DataFrame(), [], [], "", "", "")


def test_column_existence_errors(sample_unmatched, sample_heat):
    # Test missing left filter col
    with pytest.raises(
        ColumnDoesNotExistError, match="'Missing' not found in unmatched_df"
    ):
        perform_fuzzy_match(
            sample_unmatched,
            sample_heat,
            ["Missing"],
            ["DOB"],
            "External_Name",
            "Name",
            "T",
        )

    # Test missing right filter col
    with pytest.raises(ColumnDoesNotExistError, match="'Missing' not found in heat_df"):
        perform_fuzzy_match(
            sample_unmatched,
            sample_heat,
            ["Birth_Date"],
            ["Missing"],
            "External_Name",
            "Name",
            "T",
        )


def test_filter_mismatch_error(sample_unmatched, sample_heat):
    with pytest.raises(FilterColumnMismatchError):
        perform_fuzzy_match(
            sample_unmatched,
            sample_heat,
            ["Birth_Date"],
            ["DOB", "Postcode"],
            "External_Name",
            "Name",
            "T",
        )


def test_fuzzy_non_unique_index_error(sample_heat):
    df_non_unique = pd.DataFrame({"Name": ["A", "B"]}, index=[0, 0])
    with pytest.raises(FuzzyMatchIndexError):
        perform_fuzzy_match(df_non_unique, sample_heat, [], [], "Name", "Name", "T")


def test_column_collision_warning(sample_unmatched, sample_heat, capsys):
    # Add a column that triggers the warning
    sample_unmatched["Old_Score_HEAT"] = 90
    perform_fuzzy_match(
        sample_unmatched,
        sample_heat,
        ["Birth_Date"],
        ["DOB"],
        "External_Name",
        "Name",
        "T",
    )
    captured = capsys.readouterr()
    assert "WARNING" in captured.out


def test_nan_handling_in_keys(sample_heat):
    """Ensures that rows with NaNs in filter columns don't crash the grouper."""
    unmatched_nan = pd.DataFrame({"Name": ["John"], "DOB": [np.nan]})
    heat_nan = pd.DataFrame({"Name": ["John"], "DOB": [np.nan]})

    matches, _ = perform_fuzzy_match(
        unmatched_nan, heat_nan, ["DOB"], ["DOB"], "Name", "Name", "T"
    )
    # Depending on how pandas groups NaNs, this might be 0 or 1.
    # Current code handles it by tuple(row) which includes np.nan.
    assert isinstance(matches, pd.DataFrame)


@pytest.fixture
def valid_dfs():
    """Provides minimal valid DataFrames for fuzzy matching."""
    unmatched = pd.DataFrame({
        "Student_Name": ["Alice"],
        "Postcode": ["ST1 1AA"]
    })
    heat = pd.DataFrame({
        "HEAT_Name": ["Alice Smith"],
        "HEAT_Postcode": ["ST1 1AA"]
    })
    return unmatched, heat

def test_fuzzy_match_left_name_col_missing(valid_dfs):
    """Tests ColumnDoesNotExistError when left_name_col is missing from unmatched_df."""
    unmatched, heat = valid_dfs
    
    with pytest.raises(ColumnDoesNotExistError, match="'Wrong_Name' not found in unmatched_df"):
        perform_fuzzy_match(
            unmatched_df=unmatched,
            heat_df=heat,
            left_filter_cols=["Postcode"],
            right_filter_cols=["HEAT_Postcode"],
            left_name_col="Wrong_Name", # This column doesn't exist
            right_name_col="HEAT_Name",
            match_desc="Fuzzy Name Match"
        )

def test_fuzzy_match_right_name_col_missing(valid_dfs):
    """Tests ColumnDoesNotExistError when right_name_col is missing from heat_df."""
    unmatched, heat = valid_dfs
    
    with pytest.raises(ColumnDoesNotExistError, match="'Missing_HEAT_Col' not found in heat_df"):
        perform_fuzzy_match(
            unmatched_df=unmatched,
            heat_df=heat,
            left_filter_cols=["Postcode"],
            right_filter_cols=["HEAT_Postcode"],
            left_name_col="Student_Name",
            right_name_col="Missing_HEAT_Col", # This column doesn't exist
            match_desc="Fuzzy Name Match"
        )

def test_fuzzy_match_unmatched_empty(valid_dfs, capsys):
    """Tests the early exit and warning when unmatched_df is empty."""
    _, heat = valid_dfs
    # Create an empty df with the correct columns
    empty_unmatched = pd.DataFrame(columns=["Student_Name", "Postcode"])
    
    match_desc = "Fuzzy Name Match"
    
    matched, remaining = perform_fuzzy_match(
        unmatched_df=empty_unmatched,
        heat_df=heat,
        left_filter_cols=["Postcode"],
        right_filter_cols=["HEAT_Postcode"],
        left_name_col="Student_Name",
        right_name_col="HEAT_Name",
        match_desc=match_desc
    )
    
    # 1. Check Return Values
    assert matched.empty
    assert remaining.empty
    assert isinstance(matched, pd.DataFrame)
    
    # 2. Check the Warning Message
    captured = capsys.readouterr()
    assert f"WARNING: skipping match type: {match_desc}" in captured.out

# ---- FUZZY MATCHING SCHOOL DOB RANGE TESTE


@pytest.fixture
def heat_data():
    return pd.DataFrame(
        {
            "HEAT_ID": [101, 102, 103],
            "HEAT_Name": ["John Smith", "Jane Doe", "Bob Brown"],
            "HEAT_School": ["Green Abbey", "Blue Ridge", "Green Abbey"],
            "DOB": pd.to_datetime(["2010-09-01", "2011-05-05", "2010-12-12"]),
        }
    )


@pytest.fixture
def unmatched_data():
    return pd.DataFrame(
        {
            "Name": ["Jon Smith", "Jane D."],
            "School": ["Green Abbey", "Blue Ridge"],
            "YG": [10, 11],
        }
    )


# --- Happy Path & Logic Tests ---


def test_successful_school_age_match(unmatched_data, heat_data):
    """Test standard successful match including school tidying."""
    with patch("heat_helper.matching.calculate_dob_range_from_year_group") as mock_dob:
        mock_dob.return_value = (date(2010, 9, 1), date(2011, 8, 31))

        matches, remaining = perform_school_age_range_fuzzy_match(
            unmatched_data.head(1),
            heat_data,
            "School",
            "HEAT_School",
            "Name",
            "HEAT_Name",
            "YG",
            "DOB",
            "School Match",
            heat_id_col="HEAT_ID",
        )

        assert len(matches) == 1
        assert matches.iloc[0]["HEAT: HEAT_Name"] == "John Smith"
        assert len(remaining) == 0


def test_duplicate_heat_id_conflict(unmatched_data, heat_data):
    """Test that duplicate HEAT IDs are removed, keeping highest score."""
    # Two students match the same HEAT record
    unmatched_dupes = pd.DataFrame(
        {
            "Name": ["John Smith", "Jon Smith"],  # Both will match HEAT_ID 101
            "School": ["Green Abbey", "Green Abbey"],
            "YG": [10, 10],
        }
    )

    with patch("heat_helper.matching.calculate_dob_range_from_year_group") as mock_dob:
        mock_dob.return_value = (date(2010, 9, 1), date(2011, 8, 31))

        # We don't need to mock extractOne if the natural score for 'John' > 'Jon'
        matches, remaining = perform_school_age_range_fuzzy_match(
            unmatched_dupes,
            heat_data,
            "School",
            "HEAT_School",
            "Name",
            "HEAT_Name",
            "YG",
            "DOB",
            "Conflict Test",
            heat_id_col="HEAT_ID",
        )

        # Should only keep one match (the better score)
        assert len(matches) == 1
        assert len(remaining) == 1


# --- Error Handling & Branch Coverage ---


def test_input_not_dataframe():
    with pytest.raises(TypeError, match="must be pandas DataFrames"):
        perform_school_age_range_fuzzy_match([], [], "", "", "", "", "", "", "", "")


def test_dob_conversion_success(unmatched_data, heat_data):
    """Test the try/except block that converts strings to datetime."""
    heat_data["DOB"] = ["2008-01-01", "2009-05-05", "2008-12-12"]  # Strings

    matches, _ = perform_school_age_range_fuzzy_match(
        unmatched_data,
        heat_data,
        "School",
        "HEAT_School",
        "Name",
        "HEAT_Name",
        "YG",
        "DOB",
        "HEAT_ID",
        "T",
    )
    assert pd.api.types.is_datetime64_any_dtype(heat_data["DOB"])


def test_dob_conversion_failure(unmatched_data, heat_data):
    """Test the exception when DOB cannot be converted."""
    heat_data["DOB"] = ["Not a date", "Apple", "Orange"]
    with pytest.raises(TypeError, match="could not be converted"):
        perform_school_age_range_fuzzy_match(
            unmatched_data,
            heat_data,
            "School",
            "HEAT_School",
            "Name",
            "HEAT_Name",
            "YG",
            "DOB",
            "HEAT_ID",
            "T",
        )


def test_column_missing_errors_unmatched(unmatched_data, heat_data):
    with pytest.raises(ColumnDoesNotExistError, match="unmatched_df"):
        perform_school_age_range_fuzzy_match(
            unmatched_data,
            heat_data,
            "Missing",
            "HEAT_School",
            "Name",
            "HEAT_Name",
            "YG",
            "DOB",
            "HEAT_ID",
            "T",
        )

def test_column_missing_errors_heat(unmatched_data, heat_data):
    with pytest.raises(ColumnDoesNotExistError, match="heat_df"):
        perform_school_age_range_fuzzy_match(
            unmatched_data,
            heat_data,
            "School",
            "School",
            "Name",
            "HEAT_Name",
            "YG",
            "DOB",
            "HEAT_ID",
            "T",
        )


def test_non_unique_index_error(heat_data):
    bad_df = pd.DataFrame(
        {
            "Name": ["A", "B"],
            "S": ["Blank", "Blank"],
            "N": ["James", "Sarah"],
            "YG": [10, 11],
        },
        index=[0, 0],
    )
    with pytest.raises(FuzzyMatchIndexError):
        perform_school_age_range_fuzzy_match(
            bad_df,
            heat_data,
            "S",
            "HEAT_School",
            "N",
            "HEAT_Name",
            "YG",
            "DOB",
            "HID",
            "T",
        )


def test_calculate_dob_exception_skip(unmatched_data, heat_data):
    """Tests the 'continue' in the loop when calculate_dob_range fails."""
    with patch("heat_helper.matching.calculate_dob_range_from_year_group") as mock_dob:
        mock_dob.side_effect = Exception("Calculation Error")
        matches, remaining = perform_school_age_range_fuzzy_match(
            unmatched_data,
            heat_data,
            "School",
            "HEAT_School",
            "Name",
            "HEAT_Name",
            "YG",
            "DOB",
            "HEAT_ID",
            "T",
        )
        assert matches.empty
        assert len(remaining) == 2


def test_no_potential_matches_empty_block(unmatched_data, heat_data):
    """Test when a school exists but no students fall in the age range."""
    with patch("heat_helper.matching.calculate_dob_range_from_year_group") as mock_dob:
        # Range where no one was born
        mock_dob.return_value = (date(1900, 1, 1), date(1900, 1, 1))
        matches, _ = perform_school_age_range_fuzzy_match(
            unmatched_data,
            heat_data,
            "School",
            "HEAT_School",
            "Name",
            "HEAT_Name",
            "YG",
            "DOB",
            "HEAT_ID",
            "T",
        )
        assert matches.empty


def test_school_not_in_heat(unmatched_data, heat_data):
    """Test when the school name doesn't exist in the HEAT block."""
    unmatched_data.loc[0, "School"] = "Hogwarts"
    matches, _ = perform_school_age_range_fuzzy_match(
        unmatched_data.head(1),
        heat_data,
        "School",
        "HEAT_School",
        "Name",
        "HEAT_Name",
        "YG",
        "DOB",
        "HEAT_ID",
        "T",
    )
    assert matches.empty
