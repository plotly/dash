import json
import os
from collections import OrderedDict
from difflib import unified_diff

import pytest

from dash.development._py_components_generation import generate_class
from dash.development.component_generator import reserved_words
from . import _dir, expected_table_component_doc


@pytest.fixture
def component_class(load_test_metadata_json):
    return generate_class(
        typename="Table",
        props=load_test_metadata_json["props"],
        description=load_test_metadata_json["description"],
        namespace="TableComponents",
    )


@pytest.fixture
def component_written_class():
    path = os.path.join(_dir, "metadata_required_test.json")
    with open(path) as data_file:
        json_string = data_file.read()
        required_data = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(
            json_string
        )

    return generate_class(
        typename="TableRequired",
        props=required_data["props"],
        description=required_data["description"],
        namespace="TableComponents",
    )


def test_to_plotly_json(component_class):
    c = component_class()
    assert c.to_plotly_json() == {
        "namespace": "TableComponents",
        "type": "Table",
        "props": {"children": None},
    }

    c = component_class(id="my-id")
    assert c.to_plotly_json() == {
        "namespace": "TableComponents",
        "type": "Table",
        "props": {"children": None, "id": "my-id"},
    }

    c = component_class(id="my-id", optionalArray=None)
    assert c.to_plotly_json() == {
        "namespace": "TableComponents",
        "type": "Table",
        "props": {"children": None, "id": "my-id", "optionalArray": None},
    }


def test_arguments_become_attributes(component_class):
    kwargs = {"id": "my-id", "children": "text children", "optionalArray": [[1, 2, 3]]}
    component_instance = component_class(**kwargs)
    for k, v in list(kwargs.items()):
        assert getattr(component_instance, k) == v


def test_repr_single_default_argument(component_class):
    c1 = component_class("text children")
    c2 = component_class(children="text children")
    assert repr(c1) == "Table('text children')"
    assert repr(c2) == "Table('text children')"


def test_repr_single_non_default_argument(component_class):
    c = component_class(id="my-id")
    assert repr(c) == "Table(id='my-id')"


def test_repr_multiple_arguments(component_class):
    # Note how the order in which keyword arguments are supplied is
    # not always equal to the order in the repr of the component
    c = component_class(id="my id", optionalArray=[1, 2, 3])
    assert repr(c) == "Table(id='my id', optionalArray=[1, 2, 3])"


def test_repr_nested_arguments(component_class):
    c1 = component_class(id="1")
    c2 = component_class(id="2", children=c1)
    c3 = component_class(children=c2)
    assert repr(c3) == "Table(Table(children=Table(id='1'), id='2'))"


def test_repr_with_wildcards(component_class):
    c = component_class(id="1", **{"data-one": "one", "aria-two": "two"})
    data_first = "Table(id='1', data-one='one', aria-two='two')"
    aria_first = "Table(id='1', aria-two='two', data-one='one')"
    repr_string = repr(c)

    assert repr_string == data_first or repr_string == aria_first


def test_docstring(component_class):
    assert not list(
        unified_diff(expected_table_component_doc, component_class.__doc__.splitlines())
    )


def test_no_events(component_class):
    assert not hasattr(component_class, "available_events")


def test_required_props(component_written_class):
    with pytest.raises(Exception):
        component_written_class()
    component_written_class(id="test")
    with pytest.raises(Exception):
        component_written_class(id="test", lahlah="test")
    with pytest.raises(Exception):
        component_written_class(children="test")


def test_attrs_match_forbidden_props(component_class):
    assert "_.*" in reserved_words, "props cannot have leading underscores"

    # props are not added as attrs unless explicitly provided
    # except for children, which is always set if it's a prop at all.
    expected_attrs = set(reserved_words + ["children"]) - {"_.*"}
    c = component_class()
    base_attrs = set(dir(c))
    extra_attrs = set(a for a in base_attrs if a[0] != "_")

    assert (
        extra_attrs == expected_attrs
    ), "component has only underscored and reserved word attrs"

    # setting props causes them to show up as attrs
    c2 = component_class("children", id="c2", optionalArray=[1])
    prop_attrs = set(dir(c2))

    assert base_attrs - prop_attrs == set([]), "no attrs were removed"
    assert prop_attrs - base_attrs == {
        "id",
        "optionalArray",
    }, "explicit props were added as attrs"
