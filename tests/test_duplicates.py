import pytest
import pandas as pd

from heat_helper.duplicates import find_duplicates
from heat_helper.exceptions import ColumnDoesNotExistError

@pytest.fixture
def sample_df():
    """Standard dataset for testing."""
    return pd.DataFrame({
        "first_name": ["John", "Jon", "Jane", "John", "Alice"],
        "last_name": ["Doe", "Doe", "Doe", "Smith", "Brown"],
        "dob": ["1990-01-01", "1990-01-01", "1990-01-01", "1985-05-05", "1992-10-10"],
        "postcode": ["SW1 1AA", "SW1 1AA", "SW1 1AA", "E1 6AN", "N1 1LL"]
    })

## --- 1. Validation & Error Handling ---

def test_invalid_input_types():
    with pytest.raises(TypeError, match="is not a DataFrame"):
        find_duplicates("not a df", "name", "dob", "postcode")
    
    df = pd.DataFrame({"n": [1], "d": [1], "p": [1]})
    with pytest.raises(ValueError, match="Threshold must be"):
        find_duplicates(df, "n", "d", "p", threshold=150)
    
    with pytest.raises(ValueError, match="fuzzy_type must be"):
        find_duplicates(df, "n", "d", "p", fuzzy_type="invalid")

def test_column_existence_errors(sample_df):
    # Test single string name_col missing
    with pytest.raises(ColumnDoesNotExistError):
        find_duplicates(sample_df, "missing", "dob", "postcode")
    
    # Test list name_col with one item missing
    with pytest.raises(ColumnDoesNotExistError):
        find_duplicates(sample_df, ["first_name", "missing"], "dob", "postcode")
    
    # Test DOB or Postcode missing
    with pytest.raises(ColumnDoesNotExistError):
        find_duplicates(sample_df, "first_name", "wrong_dob", "postcode")
    with pytest.raises(ColumnDoesNotExistError):
        find_duplicates(sample_df, "first_name", "dob", "wrong_post")

## --- 2. Branch Coverage (Logic Paths) ---

def test_exact_matches_logic(sample_df):
    # Make two records exactly identical
    df = sample_df.copy()
    df.loc[1] = df.loc[0] 
    result = find_duplicates(df, ["first_name", "last_name"], "dob", "postcode")
    
    # Verify exact matches are caught and grouped
    # Since we sort descending, the matches should be at the top
    assert "#1, #2" in result["Potential Duplicates"].values

def test_permissive_vs_strict(sample_df):
    # Setup: Same DOB, Different Postcode
    data = {
        "name": ["John Smith", "John Smith"],
        "dob": ["1980-01-01", "1980-01-01"],
        "postcode": ["AAAA", "BBBB"]
    }
    df = pd.DataFrame(data)
    
    # Strict should find nothing
    strict_res = find_duplicates(df, "name", "dob", "postcode", fuzzy_type="strict")
    assert strict_res["Potential Duplicates"].isna().all()
    
    # Permissive should find them
    perm_res = find_duplicates(df, "name", "dob", "postcode", fuzzy_type="permissive")
    assert "#1, #2" in perm_res["Potential Duplicates"].values

def test_twin_protection_logic():
    # Setup: Same last name/dob/postcode, but different first names
    data = {
        "name": ["Robert Smith", "Thomas Smith"],
        "dob": ["1990-05-05", "1990-05-05"],
        "postcode": ["M1 1AA", "M1 1AA"]
    }
    df = pd.DataFrame(data)
    
    # With protection: Should ignore them
    prot_on = find_duplicates(df, "name", "dob", "postcode", twin_protection=True, threshold=40)
    assert prot_on["Potential Duplicates"].isna().all()
    
    # Without protection: Should flag them (Smith/Smith + same DOB is a high score)
    prot_off = find_duplicates(df, "name", "dob", "postcode", twin_protection=False, threshold=40)
    assert "#1, #2" in prot_off["Potential Duplicates"].values

def test_chaining_union_find():
    # A matches B, B matches C -> All three should be in one group
    data = {
        "name": ["Alpha", "Alphe", "Alphi"], # Fuzzy chain
        "dob": ["2000-01-01"] * 3,
        "postcode": ["Z1"] * 3
    }
    df = pd.DataFrame(data)
    result = find_duplicates(df, "name", "dob", "postcode", threshold=70)
    assert "#1, #2, #3" in result["Potential Duplicates"].values

## --- 3. Edge Cases & Cleaning ---

def test_whitespace_and_null_handling():
    data = {
        "name": ["  Clean Name  ", "Clean Name"],
        "dob": ["1990-01-01", "1990-01-01"],
        "postcode": ["SW1", "SW1"]
    }
    df = pd.DataFrame(data)
    result = find_duplicates(df, "name", "dob", "postcode")
    assert "#1, #2" in result["Potential Duplicates"].values

def test_custom_id_column(sample_df):
    sample_df["my_id"] = ["A1", "A2", "A3", "A4", "A5"]
    # Force a match
    sample_df.loc[1, "first_name"] = "John"
    result = find_duplicates(sample_df, "first_name", "dob", "postcode", id_col="my_id")
    assert "A1, A2" in result["Potential Duplicates"].values

def test_single_row_block_coverage():
    # Tests the branch: if len(block_df) < 2: continue
    data = {
        "name": ["Unique1", "Unique2"],
        "dob": ["1980-01-01", "1990-01-01"], # Different DOBs = Different blocks
        "postcode": ["A", "B"]
    }
    df = pd.DataFrame(data)
    result = find_duplicates(df, "name", "dob", "postcode")
    assert result["Potential Duplicates"].isna().all()