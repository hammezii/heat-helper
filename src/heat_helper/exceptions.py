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
        self.message = f"Invalid year group: '{value}'. Must be R/Reception or 0-13."
        super().__init__(self.message)


class FELevelError(HeatHelperError):
    """Raised when the year group input cannot be parsed or is out of range."""

    def __init__(self, value: Any):
        self.value = value
        self.message = f"Invalid year group: '{value}'. Cannot translate FE Levels to school year groups."
        super().__init__(self.message)


class InvalidPostcodeError(HeatHelperError):
    """Raised when the postcode is not a valid format."""

    def __init__(self, value: Any):
        self.value = value
        self.message = f"Invalid postcode format: '{value}'"
        super().__init__(self.message)


class ColumnDoesNotExistError(HeatHelperError):
    """Raised when a column is not found in a dataframe."""

    def __init__(self, value: Any):
        self.value = value
        self.message = f"Column does not exist: {value}"
        super().__init__(self.message)


class FuzzyMatchIndexError(HeatHelperError):
    """Raised when dataframe used for fuzzy matching does not have a unique index (which would compromise returned results.)."""

    def __init__(self, value: Any):
        self.value = value
        self.message = f"Index of {value} contains duplicate entries and cannot be used for fuzzy matching."
        super().__init__(self.message)


class FilterColumnMismatchError(HeatHelperError):
    """Raised when dataframe used for fuzzy matching does not have a unique index (which would compromise returned results.)."""

    def __init__(self, value: Any):
        self.value = value
        self.message = f"Filter columns do not match: {value}"
        super().__init__(self.message)


class ColumnsNotUnique(HeatHelperError):
    """Raised when dataframe used for fuzzy matching does not have a unique index (which would compromise returned results.)."""

    def __init__(self, value: Any):
        self.value = value
        self.message = f"Column names are not unique: {value}"
        super().__init__(self.message)
