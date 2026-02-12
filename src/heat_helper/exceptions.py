# Import internal libraries
from typing import Any


## Custom Errors
class HeatHelperError(Exception):
    """Base class for all exceptions in this package."""
    pass


class InvalidYearGroupError(HeatHelperError):
    """Raised when the year group input cannot be parsed or is out of range."""

    def __init__(self, value: Any):
        self.value = value
        super().__init__(f"Invalid year group: '{value}'. Must be R/Reception or 0-13.")


class FELevelError(HeatHelperError):
    """Raised when the year group input cannot be parsed or is out of range."""

    def __init__(self, value: Any):
        self.value = value
        super().__init__(f"Invalid year group: '{value}'. Cannot translate FE Levels to school year groups.")


class InvalidPostcodeError(HeatHelperError):
    """Raised when the postcode is not a valid format."""

    def __init__(self, value: Any):
        self.value = value
        super().__init__(f"Invalid postcode format: '{value}'")


class ColumnDoesNotExistError(HeatHelperError):
    """Raised when a column is not found in a dataframe."""

    def __init__(self, value: Any):
        self.value = value
        super().__init__(f"Column does not exist: {value}")


class FuzzyMatchIndexError(HeatHelperError):
    """Raised when dataframe used for fuzzy matching does not have a unique index (which would compromise returned results.)."""

    def __init__(self, value: Any):
        self.value = value
        super().__init__(f"Index of {value} contains duplicate entries and cannot be used for fuzzy matching.")


class FilterColumnMismatchError(HeatHelperError):
    """Raised when dataframe used for fuzzy matching does not have a unique index (which would compromise returned results.)."""

    def __init__(self, value: Any):
        self.value = value
        super().__init__(f"Filter columns do not match: {value}")


class ColumnsNotUnique(HeatHelperError):
    """Raised when dataframe used for fuzzy matching does not have a unique index (which would compromise returned results.)."""

    def __init__(self, value: Any):
        self.value = value
        super().__init__(f"Column names are not unique: {value}")
