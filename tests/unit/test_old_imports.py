from pytest import warns

from dash import dcc, dash_table


def filter_dir(package):
    ignore = [
        "warnings",
        "json",
        "async_resources",
        "package",
        "package_name",
        "f",
        "express",
        "get_plotlyjs_version",
    ]
    return sorted(
        [
            item
            for item in dir(package)
            if item == "__version__" or (item[0] not in "@_" and item not in ignore)
        ]
    )


def test_old_dcc():
    with warns(UserWarning, match="dash_core_components package is deprecated"):
        import dash_core_components as _dcc

        old_dir = filter_dir(_dcc)
        new_dir = filter_dir(dcc)

        assert old_dir == new_dir


def test_old_table():
    with warns(UserWarning, match="dash_table package is deprecated"):
        import dash_table as _dt

        old_dir = filter_dir(_dt)
        new_dir = filter_dir(dash_table)

        assert old_dir == new_dir
