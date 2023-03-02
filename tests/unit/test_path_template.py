from dash._pages import _parse_path_variables


def test_path_template_general():
    path_template = "some/<var>/static"
    assert _parse_path_variables("some/value/static", path_template) == {'var': 'value'}


def test_path_template():
    path_template = "<foo>/<bar>"
    assert _parse_path_variables("one/two", path_template) == {'foo': 'one', 'bar': 'two'}


def test_path_template_dots():
    path_template = "<foo>.<bar>"
    assert _parse_path_variables("one.two", path_template) == {'foo': 'one', 'bar': 'two'}


def test_path_template_none():
    path_template = "novars"
    assert _parse_path_variables("one/two", path_template) is None
