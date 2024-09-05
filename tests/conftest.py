import os

import pytest
import dash
from dash._configs import DASH_ENV_VARS


@pytest.fixture
def empty_environ():
    for k in DASH_ENV_VARS.keys():
        if k in os.environ:
            os.environ.pop(k)


@pytest.fixture
def clear_pages_state():
    init_pages_state()
    yield
    init_pages_state()


def init_pages_state():
    """Clear all global state that is used by pages feature."""
    dash._pages.PAGE_REGISTRY.clear()
    dash._pages.CONFIG.clear()
    dash._pages.CONFIG.__dict__.clear()
