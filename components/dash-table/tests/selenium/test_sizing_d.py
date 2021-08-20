import pytest

from test_sizing import szng003_on_prop_change_impl


@pytest.mark.parametrize(
    "fixed_columns",
    [
        # dict(),
        dict(fixed_columns=dict(headers=True)),
        dict(fixed_columns=dict(headers=True, data=1)),
    ],
)
@pytest.mark.parametrize(
    "fixed_rows",
    [
        # dict(),
        dict(fixed_rows=dict(headers=True)),
        dict(fixed_rows=dict(headers=True, data=1)),
    ],
)
@pytest.mark.parametrize(
    "merge_duplicate_headers",
    [dict(merge_duplicate_headers=True), dict(merge_duplicate_headers=False)],
)
@pytest.mark.parametrize(
    "callback_props",
    [
        dict(style_cell=dict(width=200, minWidth=200, maxWidth=200)),
    ],
)
def test_szng003_d_on_prop_change(
    test, fixed_columns, fixed_rows, merge_duplicate_headers, callback_props
):
    szng003_on_prop_change_impl(
        test, fixed_columns, fixed_rows, merge_duplicate_headers, callback_props
    )
