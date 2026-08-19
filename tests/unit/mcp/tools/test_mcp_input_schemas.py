"""Input schema generation — JSON Schema for callback input parameters.

Covers:
- Static overrides (DatePicker, Graph, Interval, Slider)
- Component introspection (representative per-type samples)
- Callback annotation overrides (highest priority)
- Required / nullable behavior
- Component type → JSON schema mapping
"""

import pytest
from typing import Optional

from dash import Dash, Input, Output, State, dcc, html
from dash.development.base_component import Component
from dash.mcp.primitives.tools.input_schemas.schema_callback_type_annotations import (
    annotation_to_json_schema,
)

from tests.unit.mcp.conftest import (
    _app_with_callback,
    _schema_for,
    _tools_list,
    _user_tool,
)


# ---------------------------------------------------------------------------
# Schema building blocks (JSON Schema primitives)
# ---------------------------------------------------------------------------

STRING = {"type": "string"}
NUMBER = {"type": "number"}
INTEGER = {"type": "integer"}
BOOLEAN = {"type": "boolean"}
NULL = {"type": "null"}
OBJECT = {"additionalProperties": True, "type": "object"}


def nullable(*schemas):
    """``{anyOf: [*schemas, {type: null}]}`` — a common nullable-type shape."""
    return {"anyOf": [*schemas, NULL]}


def array_of(*item_schemas):
    """Array of a single schema, or a union when multiple are passed."""
    items = item_schemas[0] if len(item_schemas) == 1 else {"anyOf": list(item_schemas)}
    return {"items": items, "type": "array"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_schema(component_type, prop):
    _factories = {
        "DatePickerSingle": lambda: dcc.DatePickerSingle(id="dp"),
        "DatePickerRange": lambda: dcc.DatePickerRange(id="dpr"),
        "Graph": lambda: dcc.Graph(id="graph"),
        "Interval": lambda: dcc.Interval(id="intv"),
        "Input": lambda: dcc.Input(id="inp"),
        "Textarea": lambda: dcc.Textarea(id="ta"),
        "Tabs": lambda: dcc.Tabs(id="tabs"),
        "Dropdown": lambda: dcc.Dropdown(id="dd"),
        "RadioItems": lambda: dcc.RadioItems(id="ri"),
        "Checklist": lambda: dcc.Checklist(id="cl"),
        "Store": lambda: dcc.Store(id="store"),
        "Upload": lambda: dcc.Upload(id="upload"),
        "Slider": lambda: dcc.Slider(id="sl"),
        "RangeSlider": lambda: dcc.RangeSlider(id="rs"),
    }
    app = _app_with_callback(_factories[component_type](), input_prop=prop)
    tool = _user_tool(_tools_list(app))
    return _schema_for(tool)


def _app_with_annotated_callback(annotation_type, input_prop="disabled"):
    app = Dash(__name__)
    app.layout = html.Div([dcc.Input(id="inp"), html.Div(id="out")])

    if annotation_type is None:

        @app.callback(Output("out", "children"), Input("inp", input_prop))
        def update(val):
            return str(val)

    else:

        @app.callback(Output("out", "children"), Input("inp", input_prop))
        def update(val: annotation_type):
            return str(val)

    return app


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

# (component_type, prop, expected_schema) — representative per-type samples
INTROSPECTION_CASES = [
    ("Input", "value", nullable(STRING, NUMBER)),
    (
        "Input",
        "disabled",
        nullable(
            BOOLEAN,
            {"const": "disabled", "type": "string"},
            {"const": "DISABLED", "type": "string"},
        ),
    ),
    ("Input", "n_submit", nullable(NUMBER)),
    ("Dropdown", "options", nullable({})),
    ("Checklist", "value", nullable(array_of(STRING, NUMBER, BOOLEAN))),
    ("Store", "data", nullable(OBJECT, array_of({}), NUMBER, STRING, BOOLEAN)),
    ("Upload", "contents", nullable(STRING, array_of(STRING))),
    ("RangeSlider", "value", nullable(array_of(NUMBER))),
    ("Tabs", "value", nullable(STRING)),
]

# (annotation, prop, expected_schema) — callback annotations override introspection
ANNOTATION_CASES = [
    (str, "disabled", STRING),
    (int, "value", INTEGER),
    (float, "value", NUMBER),
    (bool, "value", BOOLEAN),
    (list, "value", array_of({})),
    (dict, "value", OBJECT),
    (Optional[int], "value", nullable(INTEGER)),
    (Optional[str], "value", nullable(STRING)),
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_mcpi001_override_beats_introspection():
    """Static override wins over component introspection."""
    schema = _get_schema("DatePickerSingle", "date")
    # Introspection would return None for this prop;
    # override provides a date format with pattern
    assert schema["type"] == "string"
    assert schema["format"] == "date"
    assert "pattern" in schema


def test_mcpi013_graph_figure_uses_plotly_schema_override():
    """Graph.figure matches the FIGURE role's schema override (concrete via wildcard)."""
    schema = _get_schema("Graph", "figure")
    assert schema["type"] == "object"
    assert set(schema["properties"]) == {"data", "layout", "frames"}


@pytest.mark.parametrize(
    "component_type,prop,expected",
    INTROSPECTION_CASES,
    ids=[f"{c}.{p}" for c, p, _ in INTROSPECTION_CASES],
)
def test_mcpi002_introspected_schema(component_type, prop, expected):
    """Representative introspection tests across component types."""
    assert _get_schema(component_type, prop) == expected


@pytest.mark.parametrize(
    "ann,prop,expected",
    ANNOTATION_CASES,
    ids=[
        f"{a.__name__ if hasattr(a, '__name__') else a}-{p}"
        for a, p, _ in ANNOTATION_CASES
    ],
)
def test_mcpi003_annotation(ann, prop, expected):
    """Callback type annotations override component schemas."""
    app = _app_with_annotated_callback(ann, input_prop=prop)
    tool = _user_tool(_tools_list(app))
    assert _schema_for(tool, "val") == expected


def test_mcpi004_no_annotation_uses_introspection():
    app = _app_with_annotated_callback(None)
    tool = _user_tool(_tools_list(app))
    assert _schema_for(tool, "val") == nullable(
        BOOLEAN,
        {"const": "disabled", "type": "string"},
        {"const": "DISABLED", "type": "string"},
    )


def test_mcpi005_str_removes_null():
    app = Dash(__name__)
    app.layout = html.Div([dcc.Dropdown(id="dd"), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("dd", "value"))
    def update(val: str):
        return val

    tool = _user_tool(_tools_list(app))
    assert _schema_for(tool, "val") == STRING


def test_mcpi006_optional_preserves_null():
    app = Dash(__name__)
    app.layout = html.Div([dcc.Dropdown(id="dd"), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("dd", "value"))
    def update(val: Optional[str]):
        return val or ""

    tool = _user_tool(_tools_list(app))
    assert _schema_for(tool, "val") == nullable(STRING)


def test_mcpi007_optional_param_not_required():
    app = Dash(__name__)
    app.layout = html.Div([dcc.Dropdown(id="dd"), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("dd", "value"))
    def update(val: Optional[str]):
        return val or ""

    tool = _user_tool(_tools_list(app))
    assert "val" not in tool.inputSchema.get("required", [])


def test_mcpi008_state_annotation_overrides():
    """Annotations work for State parameters too."""
    app = Dash(__name__)
    app.layout = html.Div(
        [dcc.Input(id="inp"), dcc.Store(id="store"), html.Div(id="out")]
    )

    @app.callback(
        Output("out", "children"),
        Input("inp", "value"),
        State("store", "data"),
    )
    def update(val: str, data: dict):
        return str(val)

    tool = _user_tool(_tools_list(app))
    assert _schema_for(tool, "val") == STRING
    assert _schema_for(tool, "data") == OBJECT


def test_mcpi009_partial_annotations():
    """Some annotated, some not — introspection fills in the rest."""
    app = Dash(__name__)
    app.layout = html.Div(
        [dcc.Input(id="inp"), dcc.Store(id="store"), html.Div(id="out")]
    )

    @app.callback(
        Output("out", "children"),
        Input("inp", "value"),
        State("store", "data"),
    )
    def update(val: int, data):
        return str(val)

    tool = _user_tool(_tools_list(app))
    assert _schema_for(tool, "val") == INTEGER
    assert _schema_for(tool, "data") == nullable(
        OBJECT, array_of({}), NUMBER, STRING, BOOLEAN
    )


def test_mcpi010_component_type_maps_to_string():
    """Component annotation type maps to string schema."""
    assert annotation_to_json_schema(Component) == STRING


def test_mcpi011_dropdown_value_multi_false_narrows_to_scalar():
    """Dropdown.value with multi=False narrows to a scalar union."""
    app = _app_with_callback(dcc.Dropdown(id="dd"))
    tool = _user_tool(_tools_list(app))
    assert _schema_for(tool) == {"anyOf": [STRING, NUMBER, BOOLEAN]}


def test_mcpi012_dropdown_value_multi_true_narrows_to_array():
    """Dropdown.value with multi=True narrows to an array of scalars."""
    app = _app_with_callback(dcc.Dropdown(id="dd", multi=True))
    tool = _user_tool(_tools_list(app))
    assert _schema_for(tool) == {
        "type": "array",
        "items": {"anyOf": [STRING, NUMBER, BOOLEAN]},
    }
