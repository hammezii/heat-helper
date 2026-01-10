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

# TESTS FOR CLEAN

def test_clean_csv_logic_and_whitespace(runner, tmp_path):
    """Hits CSV branch and whitespace cleaning loop."""
    df = pd.DataFrame({
        "TextCol": ["  leading  ", "middle    spaces", "trailing  "]
    })
    file_path = tmp_path / "dirty.csv"
    df.to_csv(file_path, index=False)
    
    result = runner.invoke(main, ["clean", str(file_path)])
    
    assert result.exit_code == 0
    df_clean = pd.read_csv(tmp_path / "dirty_CLEAN.csv")
    assert df_clean["TextCol"][0] == "leading"
    assert df_clean["TextCol"][1] == "middle spaces"

def test_clean_excel_and_float_to_int(runner, tmp_path):
    """Hits Excel branch and float-to-int conversion logic."""
    df = pd.DataFrame({
        "IDs": [1.0, 2.0, 3.0, None], # Floats that are actually ints
        "Prices": [10.50, 20.99, 30.00, 5.0] # Mixed floats (logic should ignore these)
    })
    file_path = tmp_path / "test.xlsx"
    df.to_excel(file_path, index=False)
    
    result = runner.invoke(main, ["clean", str(file_path)])
    
    assert result.exit_code == 0
    # Note: Your current code saves Excel as .csv extension
    df_clean = pd.read_csv(tmp_path / "test_CLEAN.csv") 
    
    # IDs should be Int64, Prices remain floats
    inferred_int = df_clean["IDs"].dropna()
    assert (inferred_int % 1 == 0).all()

    # Alternatively, check the actual string output in the CSV 
    # to ensure it's "1" and not "1.0"
    with open(tmp_path / "test_CLEAN.csv", "r") as f: # Your code saves as .xlsx but content is CSV
        content = f.read()
        assert "1.0" not in content
        assert "1," in content or "1\n" in content

def test_clean_with_outdir(runner, tmp_path):
    """Hits the outdir branch."""
    df = pd.DataFrame({"a": [1]})
    file_path = tmp_path / "data.csv"
    df.to_csv(file_path, index=False)
    
    out_dir = tmp_path / "cleaned_output"
    os.mkdir(out_dir)
    
    result = runner.invoke(main, ["clean", str(file_path), "--outdir", str(out_dir)])
    
    assert result.exit_code == 0
    assert os.path.exists(out_dir / "data_CLEAN.csv")

def test_clean_options_headers_name_postcode(runner, tmp_path):
    # Use a very simple filename
    file_path = tmp_path / "test.csv"
    df = pd.DataFrame({
        "Full Name": ["Jöhn Doe!"],
        "Post Code": ["sw1a 1aa"]
    })
    df.to_csv(file_path, index=False)
    
    result = runner.invoke(main, [
        "clean", 
        str(file_path),
        "--headers",
        "--name", "Full Name",
        "--postcode", "Post Code"
    ])
    
    # If this fails, the output will tell us the KeyError or FileNotFoundError
    assert result.exit_code == 0, f"CLI failed with: {result.output}"
    
    # Match your CLI's naming logic: root + _CLEAN + ext
    expected_name = "test_CLEAN.csv"
    expected_path = tmp_path / expected_name
    
    assert expected_path.exists(), f"CLI Output was: {result.output}"
    
    df_clean = pd.read_csv(expected_path)
    assert "full_name" in df_clean.columns

def test_clean_unsupported_format(runner, tmp_path):
    """Hits the 'Unsupported format' return branch."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("not a csv")
    
    result = runner.invoke(main, ["clean", str(file_path)])
    assert "Unsupported format" in result.output

def test_clean_exception_handler(runner, tmp_path):
    """Hits the 'except Exception' block."""
    # Create a directory named file.csv - pandas will crash trying to read it
    bad_file = tmp_path / "crash.csv"
    os.mkdir(bad_file)
    
    result = runner.invoke(main, ["clean", str(bad_file)])
    assert "Error during cleaning" in result.output