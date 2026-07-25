---
icon: material/clock-outline
---
# Changelog
This page contains information about each release of `heat_helper`.

## v0.2.0
Release date: 2026-07-25

### ⚠️ Breaking changes

- **`create_full_name` now validates its inputs instead of failing silently.** Previously,
  passing an unsupported type returned `None` with no explanation. It now raises:
    - `TypeError` if `first_name` and `last_name` aren't both `str` or both `pd.Series`,
      or if `middle_name` doesn't match that mode;
    - `ValueError` if Series arguments differ in length, or don't share an index.
- **`create_full_name` return values changed.** Empty rows in Series mode are now `pd.NA`
  rather than `""`, and scalar mode returns `None` rather than `""` when the result is
  empty. Downstream checks like `if name == ""` need updating to `pd.isna(name)`.
- **`middle_name` now defaults to `None`** (was `""`). Omitting it, or passing `None`/`NaN`,
  all mean "no middle name" in both modes.
- **Non-whole floats in year groups now raise `InvalidYearGroupError`, not `TypeError`.**
  Affects `clean_year_group` and `calculate_dob_range_from_year_group` when called with
  `errors='raise'`. Code using `errors='coerce'` or `'ignore'` is unaffected — both
  exception types were already handled.

### Bug fixes

- **Year groups read from Excel now work.** Whole-number floats such as `7.0` are coerced
  to `7` instead of raising `TypeError` — these are common when pandas reads a numeric
  column containing blanks. `NaN` still raises `TypeError`, and genuinely fractional
  values like `6.245` are rejected as invalid year groups.
- **`perform_school_age_range_fuzzy_match` no longer modifies your DataFrame.** When
  `heat_dob_col` held strings, the automatic datetime conversion was writing back into
  the caller's frame. Input frames are now copied before any conversion happens.
- **`create_full_name` handles missing data properly.** Nulls no longer poison a whole
  row via string concatenation, and the literal string `"nan"` is treated as empty.
  A row with a missing middle name now yields `"Ann Smith"` rather than `NaN`.
- **`format_postcode` rejects malformed input earlier.** Added an explicit 5–7 character
  length guard, so inputs that are too short or too long raise `InvalidPostcodeError`
  directly rather than being reformatted into something invalid first.

### Other changes

- Fixed the type hint for `find_duplicates(id_col=...)`: `str` → `str | None`.
- Removed a dead condition in `create_error_report`'s date handling. The old
  `type(value) is not datetime.date` check compared a class against a method object and
  was always `True`; behaviour is unchanged, the code is just no longer misleading.
- Added `DEBUG` logging to the internal year-group parser, recording when a string or
  float input is coerced to an integer.

## v.0.1.3
Release date: 2026-07-24

- **Implemented Logging**: 'heat_helper' now has native logging which you can figure with the built-in 'enable_logging' function or the standard 'logging' module.

## v0.1.2
Release date: 2026-02-13

- **Bug Fix**: fixed an error with the clean year group function which meant error behaviour wasn't working correctly when run on FE Levels.

## v0.1.1
Release date: 2026-02-12

First update to `heat_helper`. 

- **Data Validation**: `pydantic` is now an optional dependency. This gives you access to a function which generates an error report by passing your data to a `pydantic` model. See [usage documentation](validation.md) or [API documentation](validation-doc.md).
- **Bug fixes**: 
    - fixed some minor issues with the duplicates function which used incorrect variable names; 
    - improved error handling in name functions; 
    - added a length guard to format_postcode; 
    - update functions now copy the DataFrame rather than editing in place.
- **Optimisations**: 
    - improved column processing in convert_to_snake_case function; 
    - get_contextual_updates now takes any Iterable for bad_values (type hints and docs updated); 
    - adding column name variables used by matching functions as constants.
    - duplicates function now has an optional twin_protection_threshold (default is 70);
    - custom exceptions updated for clarity and consistency.
- **Documentation Improvements**: reviewed docstrings and documentation for small errors, typos, and clarity and fixed all identified issues. 

## v0.1.0
Release date: 2026-01-16

Initial release of `heat_helper`.