import json

import plotly
import pytest

from dash import __version__, Dash
from dash import html
from dash.development.base_component import Component
from dash import dcc, Input, Output

Component._prop_names = ("id", "a", "children", "style")
Component._type = "TestComponent"
Component._namespace = "test_namespace"
Component._valid_wildcard_attributes = ["data-", "aria-"]


def nested_tree():
    """This tree has a few unique properties:

    - children is mixed strings and components (as in c2)
    - children is just components (as in c)
    - children is just strings (as in c1)
    - children is just a single component (as in c3, c4)
    - children contains numbers (as in c2)
    - children contains "None" items (as in c2)
    """
    c1 = Component(id="0.1.x.x.0", children="string")
    c2 = Component(
        id="0.1.x.x", children=[10, None, "wrap string", c1, "another string", 4.51]
    )
    c3 = Component(
        id="0.1.x",
        # children is just a component
        children=c2,
    )
    c4 = Component(id="0.1", children=c3)
    c5 = Component(id="0.0")
    c = Component(id="0", children=[c5, c4])
    return c, c1, c2, c3, c4, c5


def test_debc001_init():
    Component(a=3)


def test_debc002_get_item_with_children():
    c1 = Component(id="1")
    c2 = Component(children=[c1])
    assert c2["1"] == c1


def test_debc003_get_item_with_children_as_component_instead_of_list():
    c1 = Component(id="1")
    c2 = Component(id="2", children=c1)
    assert c2["1"] == c1


def test_debc004_get_item_with_nested_children_one_branch():
    c1 = Component(id="1")
    c2 = Component(id="2", children=[c1])
    c3 = Component(children=[c2])
    assert c2["1"] == c1
    assert c3["2"] == c2
    assert c3["1"] == c1


def test_debc005_get_item_with_nested_children_two_branches():
    c1 = Component(id="1")
    c2 = Component(id="2", children=[c1])
    c3 = Component(id="3")
    c4 = Component(id="4", children=[c3])
    c5 = Component(children=[c2, c4])
    assert c2["1"] == c1
    assert c4["3"] == c3
    assert c5["2"] == c2
    assert c5["4"] == c4
    assert c5["1"] == c1
    assert c5["3"] == c3


def test_debc006_get_item_with_full_tree():
    c, c1, c2, c3, c4, c5 = nested_tree()
    keys = [k for k in c]

    assert keys == ["0.0", "0.1", "0.1.x", "0.1.x.x", "0.1.x.x.0"]

    # Try to get each item
    for comp in [c1, c2, c3, c4, c5]:
        assert c[comp.id] == comp

    # Get an item that doesn't exist
    with pytest.raises(KeyError):
        c["x"]


def test_debc007_len_with_full_tree():
    c = nested_tree()[0]
    assert (
        len(c) == 5 + 5 + 1
    ), "the length of the nested children should match the total of 5 \
    components, 2 strings + 2 numbers + none in c2, and 1 string in c1"


def test_debc008_set_item_anywhere_in_tree():
    keys = ["0.0", "0.1", "0.1.x", "0.1.x.x", "0.1.x.x.0"]
    c = nested_tree()[0]

    # Test setting items starting from the innermost item
    for key in reversed(keys):
        new_id = "new {}".format(key)
        new_component = Component(id=new_id, children="new string")
        c[key] = new_component
        assert c[new_id] == new_component


def test_debc009_del_item_full_tree():
    c = nested_tree()[0]
    keys = reversed([k for k in c])
    for key in keys:
        c[key]
        del c[key]
        with pytest.raises(KeyError):
            c[key]


def test_debc010_traverse_full_tree():
    c, c1, c2, c3, c4, c5 = nested_tree()
    elements = [i for i in c._traverse()]
    assert elements == c.children + [c3] + [c2] + c2.children


def test_debc011_traverse_with_tuples():
    c, c1, c2, c3, c4, c5 = nested_tree()
    c2.children = tuple(c2.children)
    c.children = tuple(c.children)
    elements = [i for i in c._traverse()]
    assert elements == list(c.children) + [c3] + [c2] + list(c2.children)


def test_debc012_to_plotly_json_full_tree():
    c = nested_tree()[0]
    Component._namespace
    Component._type

    expected = {
        "type": "TestComponent",
        "namespace": "test_namespace",
        "props": {
            "children": [
                {
                    "type": "TestComponent",
                    "namespace": "test_namespace",
                    "props": {"id": "0.0"},
                },
                {
                    "type": "TestComponent",
                    "namespace": "test_namespace",
                    "props": {
                        "children": {
                            "type": "TestComponent",
                            "namespace": "test_namespace",
                            "props": {
                                "children": {
                                    "type": "TestComponent",
                                    "namespace": "test_namespace",
                                    "props": {
                                        "children": [
                                            10,
                                            None,
                                            "wrap string",
                                            {
                                                "type": "TestComponent",
                                                "namespace": "test_namespace",
                                                "props": {
                                                    "children": "string",
                                                    "id": "0.1.x.x.0",
                                                },
                                            },
                                            "another string",
                                            4.51,
                                        ],
                                        "id": "0.1.x.x",
                                    },
                                },
                                "id": "0.1.x",
                            },
                        },
                        "id": "0.1",
                    },
                },
            ],
            "id": "0",
        },
    }

    res = json.loads(json.dumps(c.to_plotly_json(), cls=plotly.utils.PlotlyJSONEncoder))
    assert res == expected


def test_debc013_get_item_raises_key_if_id_doesnt_exist():
    c = Component()
    with pytest.raises(KeyError):
        c["1"]

    c1 = Component(id="1")
    with pytest.raises(KeyError):
        c1["1"]

    c2 = Component(id="2", children=[c1])
    with pytest.raises(KeyError):
        c2["0"]

    c3 = Component(children="string with no id")
    with pytest.raises(KeyError):
        c3["0"]


def test_debc014_set_item():
    c1a = Component(id="1", children="Hello world")
    c2 = Component(id="2", children=c1a)
    assert c2["1"] == c1a

    c1b = Component(id="1", children="Brave new world")
    c2["1"] = c1b
    assert c2["1"] == c1b


def test_debc015_set_item_with_children_as_list():
    c1 = Component(id="1")
    c2 = Component(id="2", children=[c1])
    assert c2["1"] == c1
    c3 = Component(id="3")
    c2["1"] = c3
    assert c2["3"] == c3


def test_debc016_set_item_with_nested_children():
    c1 = Component(id="1")
    c2 = Component(id="2", children=[c1])
    c3 = Component(id="3")
    c4 = Component(id="4", children=[c3])
    c5 = Component(id="5", children=[c2, c4])

    c3b = Component(id="3")
    assert c5["3"] == c3
    assert c5["3"] != "3"
    assert c5["3"] is not c3b

    c5["3"] = c3b
    assert c5["3"] is c3b
    assert c5["3"] is not c3

    c2b = Component(id="2")
    c5["2"] = c2b
    assert c5["4"] is c4
    assert c5["2"] is not c2
    assert c5["2"] is c2b
    with pytest.raises(KeyError):
        c5["1"]


def test_debc017_set_item_raises_key_error():
    c1 = Component(id="1")
    c2 = Component(id="2", children=[c1])
    with pytest.raises(KeyError):
        c2["3"] = Component(id="3")


def test_debc018_del_item_from_list():
    c1 = Component(id="1")
    c2 = Component(id="2")
    c3 = Component(id="3", children=[c1, c2])
    assert c3["1"] == c1
    assert c3["2"] == c2
    del c3["2"]
    with pytest.raises(KeyError):
        c3["2"]
    assert c3.children == [c1]

    del c3["1"]
    with pytest.raises(KeyError):
        c3["1"]
    assert c3.children == []


def test_debc019_del_item_from_class():
    c1 = Component(id="1")
    c2 = Component(id="2", children=c1)
    assert c2["1"] == c1
    del c2["1"]
    with pytest.raises(KeyError):
        c2["1"]

    assert c2.children is None


def test_debc020_to_plotly_json_without_children():
    c = Component(id="a")
    c._prop_names = ("id",)
    c._type = "MyComponent"
    c._namespace = "basic"
    assert c.to_plotly_json() == {
        "namespace": "basic",
        "props": {"id": "a"},
        "type": "MyComponent",
    }


def test_debc021_to_plotly_json_with_null_arguments():
    c = Component(id="a")
    c._prop_names = ("id", "style")
    c._type = "MyComponent"
    c._namespace = "basic"
    assert c.to_plotly_json() == {
        "namespace": "basic",
        "props": {"id": "a"},
        "type": "MyComponent",
    }

    c = Component(id="a", style=None)
    c._prop_names = ("id", "style")
    c._type = "MyComponent"
    c._namespace = "basic"
    assert c.to_plotly_json() == {
        "namespace": "basic",
        "props": {"id": "a", "style": None},
        "type": "MyComponent",
    }


def test_debc022_to_plotly_json_with_children():
    c = Component(id="a", children="Hello World")
    c._prop_names = ("id", "children")
    c._type = "MyComponent"
    c._namespace = "basic"
    assert c.to_plotly_json() == {
        "namespace": "basic",
        "props": {
            "id": "a",
            # TODO - Rename 'children' to 'children'
            "children": "Hello World",
        },
        "type": "MyComponent",
    }


def test_debc023_to_plotly_json_with_wildcards():
    c = Component(
        id="a", **{"aria-expanded": "true", "data-toggle": "toggled", "data-none": None}
    )
    c._prop_names = ("id",)
    c._type = "MyComponent"
    c._namespace = "basic"
    assert c.to_plotly_json() == {
        "namespace": "basic",
        "props": {
            "aria-expanded": "true",
            "data-toggle": "toggled",
            "data-none": None,
            "id": "a",
        },
        "type": "MyComponent",
    }


def test_debc024_len():
    assert len(Component()) == 0
    assert len(Component(children="Hello World")) == 1
    assert len(Component(children=Component())) == 1
    assert len(Component(children=[Component(), Component()])) == 2
    assert len(Component(children=[Component(children=Component()), Component()])) == 3


def test_debc025_iter():
    # The mixin methods from MutableMapping were cute but probably never
    # used - at least not by us. Test that they're gone

    # keys, __contains__, items, values, and more are all mixin methods
    # that we get for free by inheriting from the MutableMapping
    # and behave as according to our implementation of __iter__

    c = Component(
        id="1",
        children=[
            Component(id="2", children=[Component(id="3", children=Component(id="4"))]),
            Component(id="5", children=[Component(id="6", children="Hello World")]),
            Component(),
            Component(children="Hello World"),
            Component(children=Component(id="7")),
            Component(children=[Component(id="8")]),
        ],
    )

    mixins = [
        "clear",
        "get",
        "items",
        "keys",
        "pop",
        "popitem",
        "setdefault",
        "update",
        "values",
    ]

    for m in mixins:
        assert not hasattr(c, m), "should not have method " + m

    keys = ["2", "3", "4", "5", "6", "7", "8"]

    for k in keys:
        # test __contains__()
        assert k in c, "should find key " + k
        # test __getitem__()
        assert c[k].id == k, "key {} points to the right item".format(k)

    # test __iter__()
    keys2 = []
    for k in c:
        keys2.append(k)
        assert k in keys, "iteration produces key " + k

    assert len(keys) == len(keys2), "iteration produces no extra keys"


def test_debc026_component_not_children():
    children = [Component(id="a"), html.Div(id="b"), "c", 1]
    for i in range(len(children)):
        # cycle through each component in each position
        children = children[1:] + [children[0]]

        # use html.Div because only real components accept positional args
        html.Div(children)
        # the first arg is children, and a single component works there
        html.Div(children[0], id="x")

        with pytest.raises(TypeError):
            # If you forget the `[]` around children you get this:
            html.Div(children[0], children[1], children[2], children[3])


def test_debc027_component_error_message():
    with pytest.raises(TypeError) as e:
        Component(asdf=True)
    assert str(e.value) == (
        "The `TestComponent` component received an unexpected "
        + "keyword argument: `asdf`\nAllowed arguments: a, children, "
        + "id, style"
    )

    with pytest.raises(TypeError) as e:
        Component(asdf=True, id="my-component")
    assert str(e.value) == (
        "The `TestComponent` component "
        + 'with the ID "my-component" received an unexpected '
        + "keyword argument: `asdf`\nAllowed arguments: a, children, "
        + "id, style"
    )

    with pytest.raises(TypeError) as e:
        html.Div(asdf=True)
    assert str(e.value) == (
        "The `html.Div` component (version {}) ".format(__version__)
        + "received an unexpected "
        + "keyword argument: `asdf`\n"
        + "Allowed arguments: {}".format(", ".join(sorted(html.Div()._prop_names)))
    )

    with pytest.raises(TypeError) as e:
        html.Div(asdf=True, id="my-component")
    assert str(e.value) == (
        "The `html.Div` component (version {}) ".format(__version__)
        + 'with the ID "my-component" received an unexpected '
        + "keyword argument: `asdf`\n"
        + "Allowed arguments: {}".format(", ".join(sorted(html.Div()._prop_names)))
    )


def test_debc028_set_random_id():
    app = Dash(__name__)

    input1 = dcc.Input(value="Hello Input 1")
    input2 = dcc.Input(value="Hello Input 2")
    output1 = html.Div()
    output2 = html.Div()
    output3 = html.Div(id="output-3")

    app.layout = html.Div([input1, input2, output1, output2, output3])

    @app.callback(Output(output1, "children"), Input(input1, "value"))
    def update(v):
        return f"Input 1 {v}"

    @app.callback(Output(output2, "children"), Input(input2, "value"))
    def update(v):
        return f"Input 2 {v}"

    @app.callback(
        Output(output3, "children"), Input(input1, "value"), Input(input2, "value")
    )
    def update(v1, v2):
        return f"Output 3 - Input 1: {v1}, Input 2: {v2}"

    # Verify the auto-generated IDs are stable
    assert output1.id == "e3e70682-c209-4cac-629f-6fbed82c07cd"
    assert input1.id == "82e2e662-f728-b4fa-4248-5e3a0a5d2f34"
    assert output2.id == "d4713d60-c8a7-0639-eb11-67b367a9c378"
    assert input2.id == "23a7711a-8133-2876-37eb-dcd9e87a1613"
    # we make sure that the if the id is set explicitly, then it is not replaced by random id
    assert output3.id == "output-3"


def test_debc029_random_id_errors():
    app = Dash(__name__)

    input1 = dcc.Input(value="Hello Input 1", persistence=True)
    output1 = html.Div()

    app.layout = html.Div([input1, output1])

    with pytest.raises(RuntimeError) as e:

        @app.callback(Output(output1, "children"), Input(input1, "value"))
        def update(v):
            return f"Input 1 {v}"

    assert "persistence" in e.value.args[0]
    assert "Please assign an explicit ID" in e.value.args[0]
    assert "dash_core_components.Input" in e.value.args[0]

    input1.id = "explicit"

    # now it works without error
    @app.callback(Output(output1, "children"), Input(input1, "value"))
    def update2(v):
        return f"Input 1 {v}"


def test_debc030_invalid_children_args():
    with pytest.raises(TypeError):
        dcc.Input(children="invalid children")
