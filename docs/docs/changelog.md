# Changelog
This page contains information about each release of `heat_helper`.

## v0.1.1
Release date: 2026-02-12

First update to `heat_helper`. 

- **Data Validation**: `pydantic` is now an optional dependency. This gives you access to a function which generates an error report by passing your data to a `pydantic` model. See [usage documentation](validation.md) or [API documentation](validation-doc.md).
- **Bug fixes**: 
    - fixed some minor issues with the duplicates function which used incorrect variable names; 
    - improved error handling in name functions; added a length guard to format_postcode; 
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