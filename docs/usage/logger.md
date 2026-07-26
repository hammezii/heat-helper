---
icon: material/math-log
---
# Logger
'heat_helper' has it's own built in logger. The library provides functions to enable and disable logging, or you can configure it using the standard 'logging' module.

Log levels used by this package:
- **DEBUG**: Per-value decisions (a value coerced to None, a fallback taken). May fire once per row when applied to a pandas Series.
- **INFO**: One-per-call summaries of Series/DataFrame-wide operations.
- **WARNING**: Non-fatal problems the caller almost certainly wants to know about. **Shown by default.**

Note: DEBUG records may include the data values being processed, which for this package can mean student names, dates of birth and postcodes. DEBUG is off by default and should be enabled deliberately.

## What you see without doing anything
Warnings are shown by default, because they report problems that can corrupt a HEAT upload — for example the same HEAT Student ID being matched to two different students. You do not need to turn logging on to see them. INFO and DEBUG stay quiet until you ask for them.

Until you call `enable_logging()` these warnings appear as plain text with no level or module name in front of them, which is how Python reports log messages from a library you haven't configured. Turn the logger on to get the full formatting.

!!! Note
    If you have already configured logging yourself — with `enable_logging()`, `logging.basicConfig()`, or your own handler — your configuration takes over completely and nothing is shown twice.

If you want 'heat_helper' to be completely silent, including warnings, add a null handler to its logger:

=== "Example: silence the package entirely"

    ```python

    import logging

    logging.getLogger("heat_helper").addHandler(logging.NullHandler())

    ```

## Enable Logger
Turn the logger on to see progress reports as well as warnings, and to get level and module names on every line. By default, the logger level is set to INFO and will stream to `sys.stderr` which matches standard logging behaviour. You can also set your own format, which is set to '%(levelname)s %(name)s: %(message)s' by default.

=== "Example: enable logger"

    ```python

    import heat_helper as hh

    hh.enable_logging(level="DEBUG")

    hh.format_name(123, errors="coerce")
    
    DEBUG heat_helper.names: format_name: non-string input 123 coerced to None
    ```

## Disable Logger
Removes the handler added by `enable_logging()` and restores the default behaviour, where records propagate to whatever logging the host application has configured.

!!! Note
    This restores the default rather than making the package completely silent: INFO and DEBUG stop, but warnings remain visible. See [above](#what-you-see-without-doing-anything) if you want to silence warnings too.

=== "Example: disable logger"

    ```python

    import heat_helper as hh

    hh.disable_logging()

    ```