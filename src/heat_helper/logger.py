import logging
import sys
from typing import TextIO

"""
heat_helper follows the standard library-logging convention: it emits log
records but never configures logging itself. By default the package is
completely silent. Users opt in with `heat_helper.enable_logging()`, or by
configuring the "heat_helper" logger through the standard `logging` module.

Log levels used by this package:
    DEBUG    Per-value decisions (a value coerced to None, a fallback taken).
             May fire once per row when applied to a pandas Series.
    INFO     One-per-call summaries of Series/DataFrame-wide operations.
    WARNING  Non-fatal problems the caller almost certainly wants to know about.

Note: DEBUG records may include the data values being processed, which for
this package can mean student names, dates of birth and postcodes. DEBUG is
off by default and should be enabled deliberately.
"""

PACKAGE_LOGGER_NAME = "heat_helper"

# Default format for enable_logging().
DEFAULT_FORMAT = "%(levelname)s %(name)s: %(message)s"

# Marker attribute used to recognise the handler that enable_logging() added,
# so that repeated calls replace it rather than stacking up duplicates.
_HANDLER_FLAG = "_heat_helper_handler"


def _package_logger() -> logging.Logger:
    """Returns the top-level 'heat_helper' logger."""
    return logging.getLogger(PACKAGE_LOGGER_NAME)

# Attach a NullHandler at import time. This is the ONLY import-time side
# effect in this module. It stops Python's "last resort" handler from writing
# unconfigured WARNING+ records to stderr, without producing any output of its
# own. It does not prevent a user's own handlers from working.
_package_logger().addHandler(logging.NullHandler())


def get_logger(name: str) -> logging.Logger:
    """Returns the logger for a heat_helper submodule.

    Internal helper. Every module in the package should call this once at
    module level with `__name__`, e.g. `logger = get_logger(__name__)`, which
    produces a logger named 'heat_helper.names', 'heat_helper.dates' and so on.

    Args:
        name: The module name, normally `__name__`.

    Returns:
        A logger whose records propagate to the 'heat_helper' logger.
    """
    return logging.getLogger(name)


def _remove_existing_handler(logger: logging.Logger) -> None:
    """Removes any handler previously added by enable_logging()."""
    for handler in list(logger.handlers):
        if getattr(handler, _HANDLER_FLAG, False):
            logger.removeHandler(handler)
            handler.close()


def enable_logging(
    level: int | str = "INFO",
    *,
    fmt: str | None = None,
    stream: TextIO | None = None,
) -> logging.Logger:
    """Turns on heat_helper's log output.

    heat_helper is silent by default. Call this to see what the cleaning and
    matching functions are doing - particularly useful when using
    `errors='coerce'`, where values are silently converted to None.

    Only the 'heat_helper' logger is touched; the root logger and any logging
    your own application has configured are left alone. Calling this function
    more than once replaces the previous handler rather than adding a second,
    so it is safe to re-run in a notebook cell.

    Args:
        level (optional): Minimum level to show. Accepts a name ('DEBUG',
            'INFO', 'WARNING') or a `logging` constant. Defaults to 'INFO',
            which shows one summary line per Series operation. Use 'DEBUG' to
            see per-value decisions. Note that DEBUG output includes the data
            values themselves, which may be personal data.
        fmt (optional): A `logging` format string. Defaults to
            '%(levelname)s %(name)s: %(message)s'.
        stream (optional): Where to write. Defaults to `sys.stderr`, matching
            standard logging behaviour.

    Raises:
        ValueError: Raised if `level` is not a valid logging level name.

    Returns:
        The configured 'heat_helper' logger, so it can be tuned further.

    Example:
        >>> import heat_helper as hh
        >>> hh.enable_logging("DEBUG")
        >>> hh.format_name(123, errors="coerce")
        DEBUG heat_helper.names: format_name: non-string input 123 coerced to None
    """
    logger = _package_logger()

    # logging.Logger.setLevel accepts a string, but raises a confusing
    # ValueError for a bad one. Normalise and fail with a clear message.
    if isinstance(level, str):
        resolved = logging.getLevelName(level.upper())
        if not isinstance(resolved, int):
            raise ValueError(
                f"'{level}' is not a valid logging level. "
                "Use 'DEBUG', 'INFO', 'WARNING', 'ERROR' or 'CRITICAL'."
            )
        level = resolved

    _remove_existing_handler(logger)

    handler = logging.StreamHandler(stream if stream is not None else sys.stderr)
    handler.setFormatter(logging.Formatter(fmt or DEFAULT_FORMAT))
    handler.setLevel(level)
    setattr(handler, _HANDLER_FLAG, True)

    logger.addHandler(handler)
    logger.setLevel(level)

    # Stop records reaching the root logger as well. Without this, a user who
    # has already called logging.basicConfig() would see every heat_helper
    # message twice - once from our handler, once from theirs.
    logger.propagate = False

    return logger


def disable_logging() -> logging.Logger:
    """Turns heat_helper's log output back off.

    Removes the handler added by `enable_logging()` and restores the default
    behaviour, where records propagate to whatever logging the host
    application has configured. Safe to call when logging was never enabled.

    Returns:
        The 'heat_helper' logger.
    """
    logger = _package_logger()
    _remove_existing_handler(logger)
    logger.setLevel(logging.NOTSET)
    logger.propagate = True
    return logger


def log_series_summary(
    logger: logging.Logger, func_name: str, total: int, **counts: int
) -> None:
    """Emits a single INFO summary line for a Series-wide operation.

    Internal helper. Keeps the summary wording identical across modules, and
    keeps the per-row DEBUG records and the aggregate INFO record consistent.

    Args:
        logger: The calling module's logger.
        func_name: Name of the function reporting, e.g. 'reverse_date'.
        total: Number of values processed.
        **counts: Named outcome counts, e.g. `parsed=9812, unresolved=188`.
            Underscores in the names are rendered as spaces. Zero counts are
            omitted from the message.

    Example:
        INFO heat_helper.dates: calculate_dob_range_from_year_group:
        10000 values processed (9812 parsed, 188 unresolved)
    """
    # Guard on isEnabledFor so the string work below is skipped entirely when
    # INFO is not being emitted.
    if not logger.isEnabledFor(logging.INFO):
        return

    detail = ", ".join(
        f"{n} {label.replace('_', ' ')}" for label, n in counts.items() if n
    )
    logger.info(
        "%s: %d values processed%s",
        func_name,
        total,
        f" ({detail})" if detail else "",
    )