"""Tests for heat_helper's logging behaviour.

The default-configuration behaviour (Python's "last resort" handler making
WARNING+ visible when nothing else is configured) cannot be tested in-process:
pytest installs its own handlers on the root logger, which is exactly the
condition that switches the last resort handler off. Those tests therefore run
a snippet in a fresh interpreter and inspect its stderr.
"""

import io
import logging
import subprocess
import sys
import textwrap

import pytest

from heat_helper.logger import (
    DEFAULT_FORMAT,
    PACKAGE_LOGGER_NAME,
    _HANDLER_FLAG,
    disable_logging,
    enable_logging,
    get_logger,
    log_series_summary,
)


# --- Helpers ---


# Emits one WARNING and one INFO record from a real package module, so these
# tests exercise the same path a user's call would.
_EMIT = """
import pandas as pd, heat_helper as hh
u = pd.DataFrame({"Name": ["Jon Smith", "Jonathan Smyth"], "DOB": ["2013-11-01"] * 2})
h = pd.DataFrame({"Name": ["Jonathan Smith"], "DOB": ["2013-11-01"],
                  "Student HEAT ID": ["H1"]})
hh.perform_fuzzy_match(u, h, ["DOB"], ["DOB"], "Name", "Name", "T",
                       threshold=70, heat_id_col="Student HEAT ID")
"""

WARNING_TEXT = "matched to more than one student row"
INFO_TEXT = "students found in HEAT data"


def run_in_fresh_interpreter(setup: str = "") -> str:
    """Runs the emitting snippet in a new interpreter and returns its stderr."""
    result = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(setup) + _EMIT],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stderr


# --- Default behaviour: no configuration at all ---


def test_warning_visible_without_any_configuration():
    """The whole point: a data-integrity warning is not silent by default."""
    stderr = run_in_fresh_interpreter()

    assert WARNING_TEXT in stderr


def test_warning_appears_exactly_once_without_configuration():
    stderr = run_in_fresh_interpreter()

    assert stderr.count(WARNING_TEXT) == 1


def test_info_stays_silent_without_any_configuration():
    """Only WARNING and above surface by default; INFO chatter does not."""
    stderr = run_in_fresh_interpreter()

    assert INFO_TEXT not in stderr


def test_no_handler_attached_at_import():
    """A handler here - including a NullHandler - would suppress the fallback."""
    assert logging.getLogger(PACKAGE_LOGGER_NAME).handlers == []


# --- Users who configure logging keep control ---


def test_basic_config_wins_and_does_not_duplicate():
    stderr = run_in_fresh_interpreter(
        """
        import logging
        logging.basicConfig(level=logging.INFO,
                            format="APP %(levelname)s %(name)s: %(message)s")
        """
    )

    assert stderr.count(WARNING_TEXT) == 1
    assert "APP WARNING heat_helper.matching:" in stderr
    # Their level, not ours - INFO now shows because they asked for it
    assert INFO_TEXT in stderr


def test_enable_logging_does_not_duplicate():
    stderr = run_in_fresh_interpreter(
        """
        import heat_helper as hh
        hh.enable_logging()
        """
    )

    assert stderr.count(WARNING_TEXT) == 1
    assert "WARNING heat_helper.matching:" in stderr


def test_enable_logging_after_basic_config_does_not_duplicate():
    """enable_logging() sets propagate = False to avoid a second copy."""
    stderr = run_in_fresh_interpreter(
        """
        import logging, heat_helper as hh
        logging.basicConfig(level=logging.INFO)
        hh.enable_logging()
        """
    )

    assert stderr.count(WARNING_TEXT) == 1


def test_user_can_silence_package_with_null_handler():
    stderr = run_in_fresh_interpreter(
        """
        import logging
        logging.getLogger("heat_helper").addHandler(logging.NullHandler())
        """
    )

    assert WARNING_TEXT not in stderr


def test_user_can_silence_package_by_raising_level():
    stderr = run_in_fresh_interpreter(
        """
        import logging
        logging.getLogger("heat_helper").setLevel(logging.CRITICAL)
        """
    )

    assert WARNING_TEXT not in stderr


def test_disable_logging_leaves_warnings_visible():
    """Documented behaviour: 'disable' means back to default, not silent."""
    stderr = run_in_fresh_interpreter(
        """
        import heat_helper as hh
        hh.enable_logging()
        hh.disable_logging()
        """
    )

    assert stderr.count(WARNING_TEXT) == 1
    assert INFO_TEXT not in stderr


# --- get_logger ---


def test_get_logger_is_child_of_package_logger():
    logger = get_logger("heat_helper.names")

    assert logger.name == "heat_helper.names"
    assert logger.parent is logging.getLogger(PACKAGE_LOGGER_NAME)


# --- enable_logging ---


def test_enable_logging_writes_to_given_stream():
    stream = io.StringIO()

    enable_logging("INFO", stream=stream)
    get_logger("heat_helper.test").info("hello")

    assert "INFO heat_helper.test: hello" in stream.getvalue()


def test_enable_logging_respects_custom_format():
    stream = io.StringIO()

    enable_logging("INFO", fmt="[%(levelname)s] %(message)s", stream=stream)
    get_logger("heat_helper.test").info("hello")

    assert "[INFO] hello" in stream.getvalue()


def test_enable_logging_default_format_is_documented_one():
    stream = io.StringIO()

    enable_logging("INFO", stream=stream)
    get_logger("heat_helper.test").warning("careful")

    assert DEFAULT_FORMAT % {
        "levelname": "WARNING",
        "name": "heat_helper.test",
        "message": "careful",
    } in stream.getvalue()


def test_enable_logging_level_filters_debug_by_default():
    stream = io.StringIO()

    enable_logging("INFO", stream=stream)
    get_logger("heat_helper.test").debug("noisy")

    assert stream.getvalue() == ""


def test_enable_logging_debug_level_shows_debug():
    stream = io.StringIO()

    enable_logging("DEBUG", stream=stream)
    get_logger("heat_helper.test").debug("noisy")

    assert "noisy" in stream.getvalue()


def test_enable_logging_accepts_logging_constant():
    stream = io.StringIO()

    enable_logging(logging.WARNING, stream=stream)
    get_logger("heat_helper.test").info("quiet")
    get_logger("heat_helper.test").warning("loud")

    assert "quiet" not in stream.getvalue()
    assert "loud" in stream.getvalue()


def test_enable_logging_is_case_insensitive():
    stream = io.StringIO()

    enable_logging("debug", stream=stream)
    get_logger("heat_helper.test").debug("noisy")

    assert "noisy" in stream.getvalue()


def test_enable_logging_invalid_level_raises():
    with pytest.raises(ValueError, match="is not a valid logging level"):
        enable_logging("VERBOSE")


def test_enable_logging_twice_does_not_duplicate_handler():
    """Safe to re-run in a notebook cell."""
    stream = io.StringIO()

    enable_logging("INFO", stream=stream)
    enable_logging("INFO", stream=stream)
    get_logger("heat_helper.test").info("once")

    logger = logging.getLogger(PACKAGE_LOGGER_NAME)
    assert sum(getattr(h, _HANDLER_FLAG, False) for h in logger.handlers) == 1
    assert stream.getvalue().count("once") == 1


def test_enable_logging_stops_propagation():
    enable_logging("INFO", stream=io.StringIO())

    assert logging.getLogger(PACKAGE_LOGGER_NAME).propagate is False


def test_enable_logging_returns_package_logger():
    logger = enable_logging("INFO", stream=io.StringIO())

    assert logger is logging.getLogger(PACKAGE_LOGGER_NAME)


# --- disable_logging ---


def test_disable_logging_removes_handler_and_restores_propagation():
    enable_logging("INFO", stream=io.StringIO())

    logger = disable_logging()

    assert not any(getattr(h, _HANDLER_FLAG, False) for h in logger.handlers)
    assert logger.propagate is True
    assert logger.level == logging.NOTSET


def test_disable_logging_stops_output():
    stream = io.StringIO()
    enable_logging("INFO", stream=stream)

    disable_logging()
    get_logger("heat_helper.test").info("after disable")

    assert "after disable" not in stream.getvalue()


def test_disable_logging_safe_when_never_enabled():
    logger = disable_logging()

    assert logger is logging.getLogger(PACKAGE_LOGGER_NAME)


def test_disable_logging_leaves_user_handlers_alone():
    """Only the handler enable_logging() added is removed."""
    logger = logging.getLogger(PACKAGE_LOGGER_NAME)
    user_handler = logging.StreamHandler(io.StringIO())
    logger.addHandler(user_handler)
    enable_logging("INFO", stream=io.StringIO())

    try:
        disable_logging()
        assert user_handler in logger.handlers
    finally:
        logger.removeHandler(user_handler)


# --- log_series_summary ---


def test_log_series_summary_formats_counts():
    stream = io.StringIO()
    enable_logging("INFO", stream=stream)

    log_series_summary(
        get_logger("heat_helper.test"), "reverse_date", 10000, parsed=9812, unresolved=188
    )

    assert (
        "reverse_date: 10000 values processed (9812 parsed, 188 unresolved)"
        in stream.getvalue()
    )


def test_log_series_summary_omits_zero_counts():
    stream = io.StringIO()
    enable_logging("INFO", stream=stream)

    log_series_summary(
        get_logger("heat_helper.test"), "format_name", 5, parsed=5, unresolved=0
    )

    assert "5 parsed" in stream.getvalue()
    assert "unresolved" not in stream.getvalue()


def test_log_series_summary_with_no_counts():
    stream = io.StringIO()
    enable_logging("INFO", stream=stream)

    log_series_summary(get_logger("heat_helper.test"), "format_name", 5)

    assert "format_name: 5 values processed" in stream.getvalue()


def test_log_series_summary_silent_when_info_disabled():
    stream = io.StringIO()
    enable_logging("WARNING", stream=stream)

    log_series_summary(get_logger("heat_helper.test"), "format_name", 5, parsed=5)

    assert stream.getvalue() == ""
