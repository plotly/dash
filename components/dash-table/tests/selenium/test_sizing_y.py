import pytest

from test_sizing import on_focus

from utils import (
    basic_modes,
    generate_markdown_mock_data,
)


@pytest.mark.parametrize("props", basic_modes)
@pytest.mark.parametrize(
    "data_fn",
    [generate_markdown_mock_data],
)
def test_szng005_on_focus(test, props, data_fn):
    on_focus(test, props, data_fn)
