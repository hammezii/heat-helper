import pytest
from heat_helper.core import (
    get_excel_filepaths_in_folder,
)


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
    d = 'example_folder'
    with pytest.raises(FileNotFoundError, match=f"The directory '{d}' does not exist."):
        get_excel_filepaths_in_folder(str(d))

def test_get_excel_filepaths_empty(tmp_path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    
    result = get_excel_filepaths_in_folder(str(empty_dir))
    
    assert result == []