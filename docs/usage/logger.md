---
icon: material/math-log
---
# Logger
'heat_helper' has it's own built in logger, which is silent by default. The library providers functions to enable and disable logging, or you can configure it using the standard 'logging' module.

Log levels used by this package:
- **DEBUG**    Per-value decisions (a value coerced to None, a fallback taken).
             May fire once per row when applied to a pandas Series.
- **INFO**     One-per-call summaries of Series/DataFrame-wide operations.
- **WARNING**  Non-fatal problems the caller almost certainly wants to know about.

Note: DEBUG records may include the data values being processed, which for this package can mean student names, dates of birth and postcodes. DEBUG is off by default and should be enabled deliberately.

## Enable Logger

## Disable Logger