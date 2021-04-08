import collections
import json
import os
import shutil

import pytest

from dash.development._py_components_generation import generate_class
from dash.development.base_component import Component
from dash.development.component_loader import load_components, generate_classes

METADATA_PATH = "metadata.json"

METADATA_STRING = """{
    "MyComponent.react.js": {
        "props": {
            "foo": {
                "type": {
                    "name": "number"
                },
                "required": false,
                "description": "Description of prop foo.",
                "defaultValue": {
                    "value": "42",
                    "computed": false
                }
            },
            "children": {
                "type": {
                    "name": "object"
                },
                "description": "Children",
                "required": false
            },
            "data-*": {
                "type": {
                    "name": "string"
                },
                "description": "Wildcard data",
                "required": false
            },
            "aria-*": {
                "type": {
                    "name": "string"
                },
                "description": "Wildcard aria",
                "required": false
            },
            "bar": {
                "type": {
                    "name": "custom"
                },
                "required": false,
                "description": "Description of prop bar.",
                "defaultValue": {
                    "value": "21",
                    "computed": false
                }
            },
            "baz": {
                "type": {
                    "name": "union",
                    "value": [
                        {
                            "name": "number"
                        },
                        {
                            "name": "string"
                        }
                    ]
                },
                "required": false,
                "description": ""
            }
        },
        "description": "General component description.",
        "methods": []
    },
    "A.react.js": {
        "description": "",
        "methods": [],
        "props": {
            "href": {
                "type": {
                    "name": "string"
                },
                "required": false,
                "description": "The URL of a linked resource."
            },
            "children": {
                "type": {
                    "name": "object"
                },
                "description": "Children",
                "required": false
            }
        }
    }
}"""
METADATA = json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(
    METADATA_STRING
)


@pytest.fixture
def write_metadata_file():
    with open(METADATA_PATH, "w") as f:
        f.write(METADATA_STRING)
    yield
    os.remove(METADATA_PATH)


@pytest.fixture
def make_namespace():
    os.makedirs("default_namespace")
    init_file_path = "default_namespace/__init__.py"
    with open(init_file_path, "a"):
        os.utime(init_file_path, None)
    yield
    shutil.rmtree("default_namespace")


def test_loadcomponents(write_metadata_file):
    my_component = generate_class(
        "MyComponent",
        METADATA["MyComponent.react.js"]["props"],
        METADATA["MyComponent.react.js"]["description"],
        "default_namespace",
    )

    a_component = generate_class(
        "A",
        METADATA["A.react.js"]["props"],
        METADATA["A.react.js"]["description"],
        "default_namespace",
    )

    c = load_components(METADATA_PATH)

    my_component_kwargs = {
        "foo": "Hello World",
        "bar": "Lah Lah",
        "baz": "Lemons",
        "data-foo": "Blah",
        "aria-bar": "Seven",
        "children": "Child",
    }
    a_kwargs = {"children": "Child", "href": "Hello World"}

    assert isinstance(my_component(**my_component_kwargs), Component)

    assert repr(my_component(**my_component_kwargs)) == repr(
        c[0](**my_component_kwargs)
    )

    assert repr(a_component(**a_kwargs)) == repr(c[1](**a_kwargs))


def test_loadcomponents_from_generated_class(write_metadata_file, make_namespace):
    my_component_runtime = generate_class(
        "MyComponent",
        METADATA["MyComponent.react.js"]["props"],
        METADATA["MyComponent.react.js"]["description"],
        "default_namespace",
    )

    a_runtime = generate_class(
        "A",
        METADATA["A.react.js"]["props"],
        METADATA["A.react.js"]["description"],
        "default_namespace",
    )

    generate_classes("default_namespace", METADATA_PATH)
    from default_namespace.MyComponent import MyComponent as MyComponent_buildtime
    from default_namespace.A import A as A_buildtime

    my_component_kwargs = {
        "foo": "Hello World",
        "bar": "Lah Lah",
        "baz": "Lemons",
        "data-foo": "Blah",
        "aria-bar": "Seven",
        "children": "Child",
    }
    a_kwargs = {"children": "Child", "href": "Hello World"}

    assert isinstance(MyComponent_buildtime(**my_component_kwargs), Component)

    assert repr(MyComponent_buildtime(**my_component_kwargs)) == repr(
        my_component_runtime(**my_component_kwargs)
    )

    assert repr(a_runtime(**a_kwargs)) == repr(A_buildtime(**a_kwargs))
