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
def clear_page_registry():
    dash.page_registry.clear()
    yield
    dash.page_registry.clear()
