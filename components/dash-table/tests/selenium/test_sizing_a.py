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
        dict(
            data=[
                {"_": 0, "a": 85, "b": 601, "c": 891},
                {"_": 0, "a": 967, "b": 189, "c": 514},
                {"_": 0, "a": 398, "b": 262, "c": 743},
                {
                    "_": "SOME VERY LONG VALUE",
                    "a": "SOME VERY LONG VALUE 2",
                    "b": "SOME VERY LONG VALUE 3",
                    "c": "SOME VERY LONG VALUE 4",
                },
                {"_": 0, "a": 89, "b": 560, "c": 582},
                {"_": 0, "a": 809, "b": 591, "c": 511},
            ]
        )
    ],
)
def test_szng003_a_on_prop_change(
    test, fixed_columns, fixed_rows, merge_duplicate_headers, callback_props
):
    szng003_on_prop_change_impl(
        test, fixed_columns, fixed_rows, merge_duplicate_headers, callback_props
    )
