import pandas as pd
from datetime import datetime
from typing import Any, cast, TYPE_CHECKING
from .logger import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:
    from pydantic import BaseModel as _PydanticBaseModel, ValidationError

    _HAS_PYDANTIC = True
else:
    try:
        from pydantic import BaseModel as _PydanticBaseModel, ValidationError

        _HAS_PYDANTIC = True
    except ImportError:  # pragma: no cover

        class _PydanticBaseModel:
            pass

        class ValidationError(Exception):
            pass

        _HAS_PYDANTIC = False


def create_error_report(df: pd.DataFrame, Model: Any, df_name: str) -> pd.DataFrame:
    """Uses a Pydantic model to validate each row of a DataFrame and generates an error report. 
    Returns the original DataFrame with three new columns: 'val_error_count', 'val_error_details', and 'validation_status'.
    Note: if an empty DataFrame is accidentally passed to this function it is returned as is with no additional columns.

    Args:
        df: The DataFrame you want to validate.
        Model: Your pydantic model. Should be a subclass of BaseModel.
        df_name: Name of your DataFrame for logging purposes.

    Raises:
        ImportError: Raised if pydantic is not installed
        TypeError: Raised if df is not a DataFrame or Model is not a Pydantic BaseModel class. 
        AttributeError: Raised if Model does not have 'model_validate' method (ensures you are using Pydantic v2).

    Returns:
        Your original DataFrame with three new columns: 'val_error_count': Number of validation errors in the row (0 if valid); 'val_error_details': A string summarising the validation errors (None if valid);'validation_status': "Valid" or "Invalid"
    """
    if not _HAS_PYDANTIC:
        raise ImportError(
            "The function 'create_error_report' requires Pydantic."
            "Please install it using: pip install 'heat_helper[validation]'"
        )

    ValidatedModel = cast(Any, Model)

    # Type checks - fail fast!
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Input 'df' must be a pandas DataFrame, not {type(df)}")

    if not isinstance(Model, type):
        raise TypeError(
            f"Input 'Model' must be a Pydantic Model Class, not an instance of "
            f"{type(Model).__name__}"
        )
    if not issubclass(Model, _PydanticBaseModel):
        raise TypeError(
            f"Input 'Model' must be a subclass of pydantic.BaseModel, not "
            f"{Model.__name__}"
        )

    if not hasattr(ValidatedModel, "model_validate"):
        raise AttributeError(
            "Model does not have 'model_validate'. Are you using Pydantic V2?"
        )

    if df.empty:
        logger.warning("Skipping validation: %s is empty. Returning original dataframe.", df_name)
        return df

    # Create empty list to collect error reports
    logger.info("Attempting validation of %s...", df_name)
    list_for_joining = []

    data_dicts = df.astype(object).where(pd.notnull(df), None).to_dict(orient="records")

    for row_dict in data_dicts:
        row_dict.update(
            {
                "val_error_count": 0,
                "val_error_details": None,
                "validation_status": "Valid",
            }
        )

        try:
            # Pass clean dictionary to validation
            model_instance = ValidatedModel.model_validate(row_dict)
            cleaned_data = model_instance.model_dump(exclude_unset=False)
            row_dict.update(cleaned_data)
        except ValidationError as e:
            e = cast(Any, e)
            all_error_messages = []
            for err in e.errors():
                loc = err.get("loc")
                field = str(loc[-1]) if loc else "Model Error"
                all_error_messages.append(f"'{field}': {err.get('msg')}")
            row_dict.update(
                {
                    "val_error_count": e.error_count(),
                    "val_error_details": "; ".join(all_error_messages),
                    "validation_status": "Invalid",
                }
            )
        # Date clean up
        for key, value in row_dict.items():
            # datetime is a subclass of date; convert real datetimes/Timestamps to date
            if isinstance(value, datetime):
                try:
                    row_dict[key] = value.date()
                except AttributeError:
                    pass
        # Add row to the list to be joined
        list_for_joining.append(row_dict)

    error_report = pd.DataFrame.from_records(list_for_joining, index=df.index)
    invalid_mask = error_report["validation_status"] == "Invalid"
    error_count = invalid_mask.sum()
    total_errors = error_report["val_error_count"].sum()
    logger.info(
        "Validated %d rows in %s. %d rows have %d total errors.",
        len(error_report),
        df_name,
        error_count,
        total_errors,
    )
    return error_report
