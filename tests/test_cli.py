import pytest
from click.testing import CliRunner
from heat_helper.cli import main
import pandas as pd
import os

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def sample_csv(tmp_path):
    """Creates a temporary CSV file with known issues."""
    df = pd.DataFrame({
        "ID": [1, 2, 2],                 # Has duplicates
        "Name ": ["Alice ", "Bob", None], # Has trailing space and missing value
        "123_Bad": [1, 2, 3]             # Starts with a number
    })
    file_path = tmp_path / "test.csv"
    df.to_csv(file_path, index=False)
    return str(file_path)

def test_version_command(runner):
    """Test that the version command returns the correct string."""
    result = runner.invoke(main, ["version"])
    assert result.exit_code == 0
    assert "heat-helper version" in result.output

def test_describe_functionality(runner, sample_csv):
    """Test that describe catches the issues we built into sample_csv."""
    result = runner.invoke(main, ["describe", sample_csv])
    
    assert result.exit_code == 0
    # Check for column name warnings
    assert "123_Bad" in result.output
    # Check for whitespace warning
    assert "Yes" in result.output  # From our whitespace logic
    # Check for duplicate count
    assert "1" in result.output  # ID has one duplicate

def test_describe_excel(runner, tmp_path):
    """Test that describe works for Excel files."""
    file_path = tmp_path / "test.xlsx"
    df = pd.DataFrame({"Data": [1, 2, 3]})
    df.to_excel(file_path, index=False)
    
    result = runner.invoke(main, ["describe", str(file_path)])
    assert result.exit_code == 0
    assert "File Type:       .xlsx" in result.output

def test_dirty_names_singular_and_plural(runner, tmp_path):
    # Case 1: One dirty name
    df1 = pd.DataFrame({"Name (Value)": [1]}) # Contains brackets
    path1 = tmp_path / "dirty1.csv"
    df1.to_csv(path1, index=False)
    
    res1 = runner.invoke(main, ["describe", str(path1)])
    assert "column name contain" in res1.output # Check singular

    # Case 2: Two dirty names
    df2 = pd.DataFrame({"Name (Value)": [1], "Age!": [2]})
    path2 = tmp_path / "dirty2.csv"
    df2.to_csv(path2, index=False)
    
    res2 = runner.invoke(main, ["describe", str(path2)])
    assert "column names contain" in res2.output # Check plural

def test_describe_invalid_file(runner, tmp_path):
    """Test the error handling when a file cannot be read."""
    # Create a directory named 'fake.csv' - pandas will fail to read this as a file
    fake_file = tmp_path / "corrupt.csv"
    os.mkdir(fake_file) 
    
    result = runner.invoke(main, ["describe", str(fake_file)])
    assert "Error reading file" in result.output

def test_unsupported_format(runner, tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("hello")
    
    result = runner.invoke(main, ["describe", str(file_path)])
    assert "Unsupported file format" in result.output

def test_describe_duplicate_headers(runner, tmp_path):
    """Test detection of duplicate column names in the raw header."""
    # Manually create a CSV string with duplicate 'ID' headers
    csv_content = "ID,Name,ID\n1,Alice,101\n2,Bob,102"
    file_path = tmp_path / "dupe_headers.csv"
    file_path.write_text(csv_content)
    
    result = runner.invoke(main, ["describe", str(file_path)])
    
    assert result.exit_code == 0
    assert "CRITICAL: Duplicate headers in raw file" in result.output
    assert "ID" in result.output