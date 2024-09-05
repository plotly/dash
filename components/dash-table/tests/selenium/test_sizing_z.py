import pytest

from test_sizing import on_focus

from utils import (
    basic_modes,
    generate_mixed_markdown_data,
)


@pytest.mark.parametrize("props", basic_modes)
def test_szng006_on_focus(test, props):
    on_focus(test, props, generate_mixed_markdown_data)
