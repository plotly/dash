import pytest

from test_sizing import on_focus

from utils import (
    basic_modes,
    generate_mock_data,
)


@pytest.mark.parametrize("props", basic_modes)
def test_szng004_on_focus(test, props):
    on_focus(test, props, generate_mock_data)
