# Import internal libraries
import re
import unicodedata

# Import external libraries
import pandas as pd

# Import helper functions
from heat_helper.core import _string_contains_int, PUNCTUATION


def format_name(text: str, errors: str = "raise") -> str | None:
    """Cleans the formatting of names. Strips extra whitespaces, converts to title case (with exceptions for names like McDonald and O'Reilly) and tidies any spaces around hyphens.

    Args:
        text: The name you wish to clean.
        errors (optional): default = 'raise' which raises all errors. 'ignore' ignores errors and returns original value, 'coerce' returns None.

    Raises:
        TypeError: Raised if text is not a string.

    Returns:
        Cleaned text.
    """
    replacements = (
        (r"\s*-\s*", "-"),  # Cleans spaces around hyphens
        (r"\s+", " "),  # Cleans any number of spaces -> one space
    )
    try:
        if not isinstance(text, str):
            raise TypeError(f"Text must be a string, not {type(text).__name__}")
        working_text = text.strip().title()
        for pattern, replacement in replacements:
            working_text = re.sub(pattern, replacement, working_text)
        # Preserves capitalisation after Mc and O' names
        working_text = re.sub(
            r"\b(Mc)([a-z])", lambda m: m.group(1) + m.group(2).upper(), working_text
        )
        working_text = re.sub(
            r"\b(O')([a-z])", lambda m: m.group(1) + m.group(2).upper(), working_text
        )
        return working_text
    except TypeError:
        if errors == 'ignore':
            return text
        if errors == "coerce":
            return None
        raise


def find_numbers_in_text(
    text: str, errors: str = "raise", convert_to_string: bool = False
) -> bool | str | None:
    """Checks if one or more numbers are present in a string. Numbers do not have to be consecutive.

    Args:
        text: the text to check for numbers.
        errors (optional): Defaults to 'raise' which raises errors. 'ignore' ignores errors and returns 'Input not string: result unknown'. 'coerce' returns None.
        convert_to_string (optional): Tells the function to convert text datatype to string, if possible. Defaults to False.

    Raises:
        TypeError: raised if input datatype is not string.

    Returns:
        Returns true if string contains one or more numbers (0-9) or false if no numbers present. returns string: 'Input not string: result unknown' if errors='ignore'.
    """
    try:
        if convert_to_string:
            text = str(text)
        if not isinstance(text, str):
            raise TypeError(f"Text must be a string, not {type(text).__name__}")
        check = _string_contains_int(text)
        return check
    except TypeError:
        if errors == "ignore":
            return "Input not string: result unknown."
        if errors == "coerce":
            return None
        raise


def remove_numbers_from_text(
    text: str, errors: str = "raise", convert_to_string: bool = False
) -> str | None:
    """Removes one or more numbers from a string (text). Numbers do not have to be consecutive.

    Args:
        text: The string you want to remove numbers from e.g. 'Jane Doe 43'
        errors (optional): Defaults to 'raise' which raises errors. 'ignore' ignores errors and returns 'Input not string: can't remove numbers'. 'coerce' returns None.
        convert_to_string (optional): Tells the function to convert text datatype to string, if possible. Defaults to False.

    Raises:
        TypeError: Raised if text is not a string.

    Returns:
        Text with numbers removed.
    """
    try:
        if convert_to_string:
            text = str(text)
        if not isinstance(text, str):
            raise TypeError(f"Text must be a string, not {type(text).__name__}")
        if _string_contains_int(text):
            clean = re.sub(r"[0-9]+", "", text)
            return clean.strip()
        else:
            return text
    except TypeError:
        if errors == "ignore":
            return "Input not string: can't remove numbers."
        if errors == "coerce":
            return None
        raise


def create_full_name(
    first_name: str | pd.Series,
    last_name: str | pd.Series,
    middle_name: str | pd.Series = "",
) -> str | pd.Series:
    """Joins strings or pandas dataFrame columns into a 'Full Name' string. Useful if you are going to be fuzzy matching names.

    Args:
        first_name: First name.
        last_name: Last name.
        middle_name (optional): Middle name. Defaults to a blank string.

    Returns:
        One string with all names joined.
    """
    if isinstance(first_name, pd.Series):
        full_name_pd = first_name + " " + middle_name + " " + last_name
        full_name_pd = full_name_pd.str.replace(r"\s+", " ", regex=True).str.strip()
        return full_name_pd
    if isinstance(first_name, str):
        name_parts = [
            str(part).strip() for part in [first_name, middle_name, last_name]
        ]
        full_name = " ".join(name_parts).strip()
        full_name = re.sub(r"\s+", " ", full_name)
        return full_name


def remove_diacritics(input_text: str, errors: str = "raise") -> str | None:
    """Removes diacritics (accented letters) from text. Uses python's built-in unicodedata library and normalises to NFKD before removal.

    Args:
        input_text: The text you want to remove diacritics from.
        errors (optional): Defaults to 'raise' which raises errors. 'ignore' ignores errors and returns original text. 'coerce' ignores errors and eturns None.

    Raises:
        TypeError: Raised if input_text is not a string.

    Returns:
        Text with accents removed e.g. 'Chloë' -> 'Chloe'.
    """
    try:
        if not isinstance(input_text, str):
            raise TypeError(f"Input must be a string, not {type(input_text).__name__}")
        nfkd_form = unicodedata.normalize("NFKD", input_text)
        return "".join([c for c in nfkd_form if unicodedata.category(c) != "Mn"])
    except:
        if errors == "coerce":
            return None
        if errors == "ignore":
            return input_text
        raise


def remove_punctuation(text: str, punctuation: str = PUNCTUATION, errors: str = 'raise') -> str | None:
    """Removes all punctuation except for hyphens and apostrophes from text. Useful for cleaning names.

    Args:
        text (str): Text you wish to remove punctuation from.
        punctuation (optional): String containing all punctuation except for hyphens and apostrophes. Can be overridden with your own version if you want to exclude other types of punctuation. Should be one string of all chars to remove.
        errors (optional): Defaults to 'raise', which raises errors. 'coerce' returns None, while 'ignore' ignores errors and returns original text.

    Raises:
        TypeError: Raised if text is not a string.

    Returns:
        Text with all punctuation except hyphens and apostrophes removed e.g. 'Jane! Doe.' -> 'Jane Doe'
    """
    try:
        if not isinstance(text, str):
            raise TypeError(f"Input must be a string, not {type(text).__name__}")
        table = str.maketrans(punctuation, " " * len(punctuation))
        text = text.strip().translate(table)
        cleaned = re.sub(r"\s+", " ", text).strip()
        return cleaned
    except:
        if errors == "coerce":
            return None
        if errors == "ignore":
            return text
        raise
