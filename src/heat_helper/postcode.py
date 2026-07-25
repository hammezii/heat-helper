# Import internal libraries
import re

# Import helper functions
from heat_helper.core import _is_valid_postcode
from heat_helper.exceptions import InvalidPostcodeError
from .logger import get_logger

logger = get_logger(__name__)


def format_postcode(postcode: str, errors: str = "raise") -> str | None:
    """Attempts to clean a postcode to conform to UK standard.

    Args:
        postcode: Text you want to clean.
        errors: default = 'raise' which raises all errors. 'ignore' returns original value, 'coerce' attempts to turn postcode into string to run the function, if can't be run returns None.

    Raises:
        TypeError: Raised if postcode is not a string.
        InvalidPostcodeError: Raised if postcode is not a valid length (5 to 7 chars).

    Returns:
        Cleaned postcode.
    """
    # checks is postcode is a string and returns original if not
    try:
        if not isinstance(postcode, str):
            if errors == "coerce":
                postcode = str(postcode)
            else:
                raise TypeError(
                    f"Postcode must be a string, not {type(postcode).__name__}"
                )

        clean = re.sub(r"\s+", "", postcode).upper().strip()

        # A UK postcode without its space is 5-7 chars (e.g. M11AA .. EC1A1BB)
        if not (5 <= len(clean) <= 7):
            raise InvalidPostcodeError(postcode)

        formatted = f"{clean[:-3]} {clean[-3:]}"
        if not _is_valid_postcode(formatted):
            raise InvalidPostcodeError(postcode)
        return formatted
        
    except (InvalidPostcodeError, TypeError):
        if errors == "ignore":
            logger.debug("format_postcode: invalid postcode or type error %r ignored, returning original", postcode)
            return postcode
        if errors == "coerce":
            logger.debug("format_postcode: invalid postcode %r coerced to None", postcode)
            return None
        raise
