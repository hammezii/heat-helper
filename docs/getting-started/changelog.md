---
icon: material/clock-outline
---
# Changelog
This page contains information about each release of `heat_helper`.

## v0.3.0
Release date: 2026-07-26

### ⚠️ Breaking changes

- **Warnings are now shown by default; the package is no longer completely silent.**
  `heat_helper` warns about problems that can corrupt a HEAT upload — the same HEAT
  Student ID matched to two different students, duplicate HEAT records, a date column
  converted automatically — and these were invisible unless you had called
  `enable_logging()`, which most users never did. The package still adds no handler and
  configures nothing: it simply no longer suppresses Python's built-in fallback for
  unhandled warnings. INFO and DEBUG are unchanged and stay silent until you ask for them.
  If you had already configured logging, nothing changes and nothing is shown twice. To
  silence the package completely, add `logging.NullHandler()` to the `"heat_helper"`
  logger. Note that `disable_logging()` now means "back to default" rather than "silent",
  so warnings survive it.
- **`perform_school_age_range_fuzzy_match` no longer discards matches that share a HEAT
  record.** Previously, when two rows both matched the same HEAT record, only the
  highest-scoring row was returned and the other was pushed into the remaining unmatched
  DataFrame — where it read as "not found in HEAT", risking a duplicate HEAT record being
  created for a student who already had one. Both rows are now returned as matches and a
  warning names the shared HEAT ID instead. This matters because the same student
  legitimately appears on more than one row when your data covers several activities, and
  every one of those rows should carry the same HEAT Student ID. If you relied on the old
  behaviour to de-duplicate, do that on the returned matches DataFrame instead.
- **`perform_exact_match` now raises `ValueError` if `heat_id_col` already exists in
  `unmatched_df`.** Matched IDs come back under the `HEAT: ` prefix, so an existing column
  of the same name was ambiguous. Drop or rename it before calling.
- **`perform_fuzzy_match` now raises `FilterColumnMismatchError` for empty filter
  columns.** Passing empty lists to `left_filter_cols`/`right_filter_cols` previously ran
  with no blocking at all; at least one column is now required.
- **`perform_school_age_range_fuzzy_match` validates all its columns before doing any
  work**, including `heat_id_col`, which was not checked at all. Missing columns now raise
  `ColumnDoesNotExistError` rather than failing later with a less helpful error.
- **Booleans are now rejected as year groups.** `clean_year_group` and
  `calculate_dob_range_from_year_group` raise `TypeError` for `True`/`False`, which were
  previously treated as the integers 1 and 0.
- **`clean_year_group(errors='ignore')` returns your original value unchanged.** It
  previously converted it to a string, so an unrecognised integer came back as `'12'`
  rather than `12`.

### Bug fixes

- **`perform_fuzzy_match` now warns when one HEAT record is matched by several rows.**
  It previously assigned the same HEAT ID to multiple rows silently, so two different
  students could be given the same ID with nothing to flag it. Matching results are
  unchanged — the warning is new. Turn on logging with `hh.enable_logging()` to see it.
- **Both fuzzy matching functions now handle a HEAT export with a duplicate index.**
  Previously this produced malformed rows in the matches DataFrame. The index of your HEAT
  DataFrame is no longer used for anything visible in the output.
- **`create_error_report` no longer misaligns results on filtered DataFrames.** The report
  columns were built with a fresh index, so validating a DataFrame whose index was not
  `0, 1, 2...` (for example one you had filtered) attached error details to the wrong rows
  or produced blanks. Results now keep your DataFrame's own index.
- **`create_error_report` gives clearer errors for a bad `Model`.** Passing an *instance*
  of a Pydantic model, or a class that is not a Pydantic model, now produces messages that
  say which of the two is wrong.
- **`find_duplicates` works with non-string ID columns.** The grouping logic joins IDs into
  strings, so passing an integer `id_col` previously produced incorrect duplicate lists.
  IDs are now normalised internally and your column is returned untouched.
- **`find_duplicates` numbers rows correctly on filtered DataFrames.** The generated
  `Duplicate ID` column was built without reference to your index, so on a DataFrame whose
  index was not `0, 1, 2...` the IDs were misaligned or missing.
- **`calculate_dob_range_from_year_group` handles an empty column.** Passing an empty
  Series now raises `ValueError` (or returns `None` under `errors='coerce'`/`'ignore'`)
  rather than failing unclearly.
- **`format_name` handles apostrophes correctly.** Possessives and initials are no longer
  given a stray capital — `"JAMES'S"` returns `"James's"`, not `"James'S"` — while
  `O'Reilly` and `McDonald` are still preserved. There is deliberately no rule for `Mac`
  names, as capitalisation of the following letter is inconsistent and cannot be inferred.
- **`enable_logging` docstring no longer shows a misleading example**, and the explanation
  of the package's logging conventions in `logger.py` is now a real module docstring.
- **The `heat_helper` logger no longer has a handler attached at import.** This was what
  suppressed warnings for unconfigured users; see the breaking change above.

### New features

- **Optional `heat_id_col` argument on `perform_fuzzy_match`.** Not used for matching —
  it only lets the shared-HEAT-record warning name the HEAT IDs affected rather than
  reporting a count. Omitting it leaves the function's behaviour exactly as before.
- **`heat_helper.create_error_report` is now resolved lazily.** Importing `heat_helper` no
  longer pulls in `validation.py` (and therefore the optional `pydantic` dependency) until
  you actually use the function, and the function keeps its own signature and docstring.

### Documentation

- Corrected the argument names (`unmatched_df`, not `new_df`) in the `perform_exact_match`
  documentation, and documented the exceptions each matching function raises.
- Documented the behaviour of `find_duplicates` with missing dates of birth or postcodes,
  and the fact that it returns rows in sorted order rather than input order. Corrected the
  threshold range and the example output in the duplicates usage page.
- Clarified `format_postcode`'s length rule (5–7 characters once spaces are removed) and
  that it also checks the UK postcode format.
- Noted that `create_error_report` returns an empty DataFrame unchanged, with no added
  columns.
- Fixed broken links in the changelog, and corrected the data validation summary in the
  README.

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

- **Implemented Logging**: 'heat_helper' now has native logging which you can figure with the built-in 'enable_logging' function or the standard 'logging' module. See [usage documentation](../usage/logger.md) or [API documentation](../api-documentation/logger-doc.md).

## v0.1.2
Release date: 2026-02-13

- **Bug Fix**: fixed an error with the clean year group function which meant error behaviour wasn't working correctly when run on FE Levels.

## v0.1.1
Release date: 2026-02-12

First update to `heat_helper`. 

- **Data Validation**: `pydantic` is now an optional dependency. This gives you access to a function which generates an error report by passing your data to a `pydantic` model. See [usage documentation](../usage/validation.md) or [API documentation](../api-documentation/validation-doc.md).
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