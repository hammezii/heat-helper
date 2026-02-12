import pytest
import pandas as pd
from datetime import datetime, date
from typing import Any
from pydantic import BaseModel
from unittest import mock
import heat_helper.validation as val
import heat_helper

# --- Mock Models ---
class SimpleModel(BaseModel):
    name: str
    age: int
    score: float | None = None
    created_at: date | None = None

class LegacyModel:
    """Simulates a non-pydantic model"""
    pass

# --- Happy Path & Logic Tests ---

def test_successful_validation():
    """Tests coercion, date cleanup, and successful validation flow."""
    df = pd.DataFrame({
        "name": ["Alice", "Bob"],
        "age": ["25", 30],  # Tests string-to-int coercion
        "score": [1.5, None],
        "created_at": [pd.Timestamp("2023-01-01"), None]
    })
    
    report = val.create_error_report(df, SimpleModel, "test_df")
    
    assert report.iloc[0]['validation_status'] == 'Valid'
    assert report.iloc[0]['age'] == 25
    assert type(report.iloc[0]['created_at']) is date
    assert report.iloc[1]['validation_status'] == 'Valid'

def test_validation_errors():
    """Tests the capture and formatting of Pydantic validation errors."""
    df = pd.DataFrame({
        "name": ["Alice", 123],
        "age": [25, "not_an_int"]
    })
    
    report = val.create_error_report(df, SimpleModel, "error_df")
    assert report.iloc[1]['validation_status'] == 'Invalid'
    assert report.iloc[1]['val_error_count'] >= 1
    assert "age" in report.iloc[1]['val_error_details']

def test_empty_dataframe():
    """Tests the early exit logic for empty DataFrames."""
    df = pd.DataFrame()
    result = val.create_error_report(df, SimpleModel, "empty_df")
    assert result.empty

def test_date_cleanup_and_edge_cases():
    """Tests datetime to date conversion and the AttributeError safety pass."""
    # Test 1: Standard datetime conversion
    df_standard = pd.DataFrame({"created_at": [datetime(2023, 1, 1, 12, 0, 0)]})
    report = val.create_error_report(df_standard, SimpleModel, "date_df")
    assert type(report.iloc[0]['created_at']) is date

    # Test 2: The AttributeError 'pass' branch (Coverage for line 84-85ish)
    fake_dt = mock.Mock(spec=datetime)
    fake_dt.date.side_effect = AttributeError("Mocked Error")
    df_fake = pd.DataFrame({"created_at": [fake_dt]})
    
    # Logic should catch error and leave object as is
    report_fake = val.create_error_report(df_fake, SimpleModel, "attr_error_df")
    assert report_fake.iloc[0]['created_at'] == fake_dt

# --- Error Handling & Defensive Guards ---

@pytest.mark.parametrize("invalid_df, invalid_model, expected_error, match_str", [
    ("not a df", SimpleModel, TypeError, "must be a pandas DataFrame"),
    (pd.DataFrame({"a": [1]}), LegacyModel, TypeError, "must be a Pydantic Model Class"),
    (pd.DataFrame({"a": [1]}), "NotAClass", TypeError, "must be a Pydantic Model Class"),
])
def test_input_guards(invalid_df, invalid_model, expected_error, match_str):
    """Consolidated test for all early-exit TypeErrors."""
    with pytest.raises(expected_error, match=match_str):
        val.create_error_report(invalid_df, invalid_model, "test")

def test_missing_pydantic_logic():
    """Tests the ImportError branch when _HAS_PYDANTIC is False."""
    df = pd.DataFrame({"a": [1]})
    with mock.patch('heat_helper.validation._HAS_PYDANTIC', False):
        with pytest.raises(ImportError, match="requires Pydantic"):
            val.create_error_report(df, SimpleModel, "test")

def test_pydantic_v2_check():
    """Tests the check for Pydantic V2 model_validate method."""
    class MockV1Model(BaseModel): pass
    df = pd.DataFrame({"name": ["Alice"]})
    
    with mock.patch("heat_helper.validation.hasattr", return_value=False):
        with pytest.raises(AttributeError, match="Are you using Pydantic V2"):
            val.create_error_report(df, MockV1Model, "legacy_test")

# --- Integration Tests ---

def test_init_lazy_load_wrapper():
    """Ensures the wrapper in __init__.py correctly passes through to validation.py."""
    df = pd.DataFrame({"id": [1]})
    class TinyModel(BaseModel): id: int

    report = heat_helper.create_error_report(df, TinyModel, "init_test")
    assert report.iloc[0]['validation_status'] == 'Valid'