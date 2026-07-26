# Import internal libraries
import re
import unicodedata

# Import external libraries
import pandas as pd

# Import helper functions
from .core import _string_contains_int, PUNCTUATION
from .logger import get_logger, log_series_summary

logger = get_logger(__name__)

def format_name(text: str, errors: str = "raise") -> str | None:
    """Cleans the formatting of names. Strips extra whitespaces, converts to title case (with exceptions for names like McDonald) and removes any spaces around hyphens.
    Converting to title case will make any letters following an apostrophe capitals so names like O'Reilly are preserved.
    There is no rule for names which begin with 'Mac' as following letter capitalisation is inconsistent and cannot be inferred.

    Args:
        text: The name you wish to clean.
        errors (optional): Default = 'raise' which raises all errors. 'ignore' ignores errors and returns original value, 'coerce' returns None.

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
        # Makes a single letter following an apostrophe lowercase
        # Preserves capitalisation after Mc names
        working_text = re.sub(
            r"(?<!\bO)'([A-Z])\b", lambda m: "'" + m.group(1).lower(), working_text
        )
        working_text = re.sub(
                    r"\b(Mc)([a-z])", lambda m: m.group(1) + m.group(2).upper(), working_text
                )

        return working_text
    except TypeError:
        if errors == "ignore":
            logger.debug("format_name: non-string input %r ignored, returning original", text)
            return text
        if errors == "coerce":
            logger.debug("format_name: non-string input %r coerced to None", text)
            return None
        raise


def find_numbers_in_text(
    text: str, errors: str = "raise", convert_to_string: bool = False
) -> bool | str | None:
    """Checks if one or more numbers are present in a string. Numbers do not have to be consecutive.

    Args:
        text: The text to check for numbers.
        errors (optional): Default = 'raise' which raises all errors. 'ignore' ignores errors and returns original value, 'coerce' returns None.
        convert_to_string (optional): Tells the function to convert text datatype to string, if possible. Defaults to False.

    Raises:
        TypeError: Raised if text datatype is not string.

    Returns:
        True if string contains one or more numbers (0-9) or False if no numbers present.
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
            logger.debug("find_numbers_in_text: non-string input %r ignored, returning original", text)
            return text
        if errors == "coerce":
            logger.debug("find_numbers_in_text: non-string input %r coerced to None", text)
            return None
        raise


def remove_numbers(
    text: str, errors: str = "raise", convert_to_string: bool = False
) -> str | None:
    """Removes one or more numbers from a string (text). Numbers do not have to be consecutive.

    Args:
        text: The string you want to remove numbers from e.g. 'Jane Doe 43'
        errors (optional): Default = 'raise' which raises all errors. 'ignore' ignores errors and returns original value, 'coerce' returns None.
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
            logger.debug("remove_numbers: non-string input %r ignored, returning original", text)
            return text
        if errors == "coerce":
            logger.debug("remove_numbers: non-string input %r coerced to None", text)
            return None
        raise


def create_full_name(
    first_name: str | pd.Series,
    last_name: str | pd.Series,
    middle_name: str | pd.Series | None = None,
) -> str | pd.Series | None:
    """Join first, (optional) middle, and last names into a full name.

    Two mutually exclusive modes:
      * DataFrame mode: first_name, last_name AND (if given) middle_name are
        all pd.Series of equal length and shared index. Returns a Series;
        rows where every part is empty become pd.NA.
      * Scalar mode: first_name and last_name are str, and (if given)
        middle_name is str. Returns a str, or None if the result is empty.

    A missing middle name (omitted, None, or NaN) is always treated as "" and a
    usable full name is built from first + last. Mixing Series and str across
    arguments is not allowed.

    Args:
        first_name: First name. str (scalar mode) or pd.Series (DataFrame mode).
        last_name: Last name. Must be the same type as first_name.
        middle_name (optional): Middle name. May be omitted or passed as
            None/NaN to mean "no middle name". Otherwise must match the mode.

    Returns:
        A joined full name: a str (or None if empty) in scalar mode, or a
        Series of strings (empty rows as pd.NA) in DataFrame mode.

    Raises:
        TypeError: On mixed argument types, or if first_name/last_name are not
            both str or both pd.Series.
        ValueError: If Series arguments differ in length or index.
    """
    first_is_series = isinstance(first_name, pd.Series)
    last_is_series = isinstance(last_name, pd.Series)

    if first_is_series != last_is_series:
        raise TypeError(
            "create_full_name: first_name and last_name must be the same type "
            f"(both str or both pd.Series); got {type(first_name).__name__} and "
            f"{type(last_name).__name__}."
        )

    series_mode = first_is_series

    # A missing middle name (omitted / None / NaN scalar) -> empty of the right kind.
    middle_absent = (
        middle_name is None
        or (isinstance(middle_name, float) and pd.isna(middle_name))
    )
    if middle_absent:
        middle_name = pd.Series("", index=first_name.index) if series_mode else ""

    # ---- DataFrame mode ----
    if series_mode:
        if not isinstance(middle_name, pd.Series):
            raise TypeError(
                "create_full_name: middle_name must be a pd.Series when "
                f"first_name and last_name are Series; got {type(middle_name).__name__}."
            )
        index = first_name.index
        for name, s in (("last_name", last_name), ("middle_name", middle_name)):
            if len(s) != len(first_name):
                raise ValueError(
                    "create_full_name: all Series must be the same length; "
                    f"'{name}' has length {len(s)}, first_name has {len(first_name)}."
                )
            if not s.index.equals(index):
                raise ValueError(
                    "create_full_name: Series arguments must share an index, but "
                    f"'{name}' differs from 'first_name'. Reset indices "
                    "(e.g. df.reset_index(drop=True)) before calling."
                )

        def _clean_part(part):
            # Coerce to text, null/blank/"nan" -> "", then strip.
            cleaned = part.astype("string").fillna("").str.strip()
            return cleaned.mask(cleaned.str.lower() == "nan", "")

        first = _clean_part(first_name)
        middle = _clean_part(middle_name)
        last = _clean_part(last_name)

        full_name_pd = (first + " " + middle + " " + last)
        full_name_pd = (
            full_name_pd.str.replace(r"\s+", " ", regex=True)
            .str.strip()
            .astype("object")
        )

        empty_mask = full_name_pd == ""
        empty_count = int(empty_mask.sum())
        full_name_pd = full_name_pd.mask(empty_mask, pd.NA)

        log_series_summary(
            logger,
            "create_full_name",
            len(full_name_pd),
            joined=len(full_name_pd) - empty_count,
            empty=empty_count,
        )
        return full_name_pd

    # ---- Scalar mode ----
    if not (isinstance(first_name, str) and isinstance(last_name, str)):
        raise TypeError(
            "create_full_name: first_name and last_name must be str or pd.Series; "
            f"got {type(first_name).__name__} and {type(last_name).__name__}."
        )
    if not isinstance(middle_name, str):
        raise TypeError(
            "create_full_name: middle_name must be str (or None) when first_name "
            f"and last_name are str; got {type(middle_name).__name__}."
        )

    parts = [p.strip() for p in (first_name, middle_name, last_name)]
    full_name = re.sub(r"\s+", " ", " ".join(parts)).strip()
    return full_name if full_name else None


def remove_diacritics(input_text: str, errors: str = "raise") -> str | None:
    """Removes diacritics (accented letters) from text. Uses python's built-in unicodedata library and normalises to NFKD before removal.

    Args:
        input_text: The text you want to remove diacritics from.
        errors (optional): Default = 'raise' which raises all errors. 'ignore' ignores errors and returns original value, 'coerce' returns None.

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
    except TypeError:
        if errors == "coerce":
            logger.debug("remove_diacritics: non-string input %r coerced to None", input_text)
            return None
        if errors == "ignore":
            logger.debug("remove_diacritics: non-string input %r ignored, returning original", input_text)
            return input_text
        raise


def remove_punctuation(
    text: str, punctuation: str = PUNCTUATION, errors: str = "raise"
) -> str | None:
    r"""Removes all punctuation except for hyphens and apostrophes from text. Useful for cleaning names.

    Args:
        text (str): Text you wish to remove punctuation from.
        punctuation (optional): String containing all punctuation except for hyphens and apostrophes. Can be overridden with your own version if you want to exclude other types of punctuation. Should be one string of all chars to remove. Default includes the following chars: !@#£$%^&*()_=+`~,.<>/?;:"\|[]
        errors (optional): Default = 'raise' which raises all errors. 'ignore' ignores errors and returns original value, 'coerce' returns None.

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
    except TypeError:
        if errors == "coerce":
            logger.debug("remove_punctuation: non-string input %r coerced to None", text)
            return None
        if errors == "ignore":
            logger.debug("remove_punctuation: non-string input %r ignored, returning original", text)
            return text
        raise
