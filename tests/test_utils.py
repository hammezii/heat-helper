import pytest
import pandas as pd

from heat_helper.utils import get_excel_filepaths_in_folder, convert_col_snake_case
from heat_helper.exceptions import ColumnsNotUnique


# --- Get Files Tests --
def test_get_files_silent_by_default(tmp_path, capsys):
    # tmp_path is a built-in pytest fixture that creates a temporary folder
    d = tmp_path / "sub-excel"
    d.mkdir()
    f = d / "test.xlsx"
    f.write_text("dummy content")

    # Run without setting print_to_terminal (defaults to False)
    get_excel_filepaths_in_folder(str(d))

    captured = capsys.readouterr()
    assert captured.out == ""  # Nothing should have been printed


def test_get_files_printing(tmp_path, capsys):
    d = tmp_path / "sub-excel-print"
    d.mkdir()
    f = d / "test.xlsx"
    f.write_text("dummy content")

    # Run with printing enabled
    get_excel_filepaths_in_folder(str(d), print_to_terminal=True)

    captured = capsys.readouterr()
    assert "Found Excel file: test.xlsx" in captured.out


def test_get_files_not_excel_printing(tmp_path, capsys):
    d = tmp_path / "sub-doc"
    d.mkdir()
    f = d / "test.docx"
    f.write_text("dummy content")

    # Run with printing enabled
    get_excel_filepaths_in_folder(str(d), print_to_terminal=True)

    captured = capsys.readouterr()
    assert "Skipping non-Excel file: test.docx" in captured.out


def test_get_files_folder_not_exist_raises_error():
    # Folder does not exist.
    d = "example_folder"
    with pytest.raises(FileNotFoundError, match=f"The directory '{d}' does not exist."):
        get_excel_filepaths_in_folder(str(d))


def test_get_excel_filepaths_empty(tmp_path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    result = get_excel_filepaths_in_folder(str(empty_dir))

    assert result == []

# -- SNAKE CASE TESTS --
def test_convert_col_snake_case_success():
    """Test standard transformation: casing, spaces, and stripping."""
    df = pd.DataFrame({
        "First Name": [1],
        "LAST   NAME": [2], # Multiple spaces
        "  Middle Name  ": [3], # Leading/trailing spaces
        "Already_Snake": [4]
    })
    
    result = convert_col_snake_case(df)
    
    # Expected: 
    # "First Name" -> "first_name"
    # "LAST   NAME" -> "last_name" (re.sub handles multiple spaces)
    # "  Middle Name  " -> "middle_name" (strip and replace)
    # "Already_Snake" -> "already_snake"
    
    expected_cols = ["first_name", "last_name", "middle_name", "already_snake"]
    assert list(result.columns) == expected_cols

def test_convert_col_snake_case_empty_df():
    """Ensures function works on a DataFrame with no columns."""
    df = pd.DataFrame()
    result = convert_col_snake_case(df)
    assert len(result.columns) == 0
    assert isinstance(result, pd.DataFrame)

def test_convert_col_snake_case_type_error():
    """Triggers the TypeError branch."""
    with pytest.raises(TypeError, match="df must be a DataFrame"): # Matches your current code typo
        convert_col_snake_case(["not", "a", "dataframe"])

def test_convert_col_snake_case_immutability():
    """Ensures the original DataFrame's columns aren't modified in-place if possible."""
    df = pd.DataFrame({"Old Col": [1]})
    result = convert_col_snake_case(df)
    
    assert "Old Col" in df.columns
    assert "old_col" in result.columns

def test_convert_col_snake_case_complex_strings():
    """Test handling of CamelCase and special characters."""
    df = pd.DataFrame({
        "FirstName": [1],
        "Cost ($)": [2],
        "Total-Amount": [3],
        "Already_Snake": [4]
    })
    result = convert_col_snake_case(df)
    
    # Expected results:
    # "FirstName" -> "first_name"
    # "Cost ($)" -> "cost"
    # "Total-Amount" -> "total_amount"
    assert "first_name" in result.columns
    assert "cost" in result.columns
    assert "total_amount" in result.columns

def test_raises_on_collision_post():
    # These are unique names, but both become 'my_col'
    df = pd.DataFrame(columns=["My Col", "My  Col"]) 
    with pytest.raises(ColumnsNotUnique, match="duplicate columns"):
        convert_col_snake_case(df)

def test_raises_on_collision_pre():
    # These are unique names, but both become 'my_col'
    df = pd.DataFrame(columns=["Name", "Name"]) 
    with pytest.raises(ColumnsNotUnique, match="duplicate columns"):
        convert_col_snake_case(df)