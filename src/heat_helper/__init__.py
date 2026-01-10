# Import utils

from .utils import get_excel_filepaths_in_folder, convert_col_snake_case

from .names import (
    format_name,
    find_numbers_in_text,
    remove_numbers_from_text,
    create_full_name,
    remove_diacritics,
)

from .dates import reverse_date, calculate_dob_range_from_year_group

from .postcode import (
    format_postcode,
)

from .yeargroup import (
    clean_year_group,
    calculate_year_group_from_date,
)

from .matching import (
    perform_exact_match,
    perform_fuzzy_match,
    perform_school_age_range_fuzzy_match,
)

from .updates import (
    get_updates,
    get_contextual_updates,
)

# Import *
__all__ = [
    "calculate_dob_range_from_year_group",
    "clean_year_group",
    "format_postcode",
    "get_excel_filepaths_in_folder",
    "format_name",
    "find_numbers_in_text",
    "remove_numbers_from_text",
    "reverse_date",
    "create_full_name",
    "remove_diacritics",
    "perform_exact_match",
    "calculate_year_group_from_date",
    "perform_fuzzy_match",
    "perform_school_age_range_fuzzy_match",
    "get_updates",
    "get_contextual_updates",
    "convert_col_snake_case",
]

# Version constant
__version__ = "0.1.3"
