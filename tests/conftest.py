import logging

import pytest

from heat_helper.logger import disable_logging


@pytest.fixture(autouse=True)
def reset_heat_helper_logging():
    """Restores heat_helper's default logging state after every test.

    enable_logging() sets propagate = False on the 'heat_helper' logger, which
    would stop pytest's caplog fixture seeing any records in later tests.
    Resetting here keeps tests independent of the order they run in.
    """
    yield
    disable_logging()
    logging.getLogger("heat_helper").setLevel(logging.NOTSET)
