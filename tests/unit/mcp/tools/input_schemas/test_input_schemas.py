"""Input schema tests — verifies JSON Schema generation for component properties.

Tests are organized by concern:
- Static overrides (date pickers, graph, interval, sliders)
- Component introspection (representative samples — full type coverage in test_json_prop_typing)
- Callback annotation overrides (highest priority)
- Required/nullable behavior
"""

import pytest
from typing import Optional

from dash import Dash, Input, Output, State, dcc, html

from tests.unit.mcp.conftest import (
    _app_with_callback,
    _schema_for,
    _tools_list,
    _user_tool,
)

# ---------------------------------------------------------------------------
# Expected schemas for static overrides
# ---------------------------------------------------------------------------

_DATE_SCHEMA = {"type": "string", "format": "date", "pattern": r"^\d{4}-\d{2}-\d{2}$"}

OVERRIDE_SCHEMAS = {
    ("DatePickerSingle", "date"): _DATE_SCHEMA,
    ("DatePickerRange", "start_date"): _DATE_SCHEMA,
    ("DatePickerRange", "end_date"): _DATE_SCHEMA,
    ("Graph", "figure"): {
        "type": "object",
        "properties": {
            "data": {"type": "array", "items": {"type": "object"}},
            "layout": {"type": "object"},
            "frames": {"type": "array", "items": {"type": "object"}},
        },
    },
    ("Graph", "clickData"): {"type": "object"},
    ("Graph", "hoverData"): {"type": "object"},
    ("Graph", "selectedData"): {"type": "object"},
    ("Graph", "relayoutData"): {"type": "object"},
    ("Graph", "restyleData"): {"type": "array"},
    ("Interval", "n_intervals"): {"type": "integer"},
    ("Slider", "marks"): {
        "type": "object",
        "additionalProperties": {
            "oneOf": [
                {"type": "string"},
                {
                    "type": "object",
                    "properties": {
                        "label": {"type": "string"},
                        "style": {"type": "object"},
                    },
                    "required": ["label"],
                },
            ]
        },
    },
    ("Slider", "tooltip"): {
        "type": "object",
        "properties": {
            "always_visible": {
                "type": "boolean",
                "description": "If true, tooltips are always visible (default: visible on hover).",
            },
            "placement": {
                "type": "string",
                "enum": [
                    "left",
                    "right",
                    "top",
                    "bottom",
                    "topLeft",
                    "topRight",
                    "bottomLeft",
                    "bottomRight",
                ],
                "description": "Tooltip placement relative to the handle.",
            },
            "template": {
                "type": "string",
                "description": (
                    "Template string for the tooltip. Must contain "
                    "{value} which is replaced with the slider value."
                ),
            },
            "transform": {
                "type": "string",
                "description": (
                    "Name of a function in window.dccFunctions "
                    "to transform the displayed value."
                ),
            },
            "style": {
                "type": "object",
                "description": "CSS style for the tooltip.",
            },
        },
    },
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_COMPONENTS = {
    "DatePickerSingle": ("dp", lambda **kw: dcc.DatePickerSingle(id="dp", **kw)),
    "DatePickerRange": ("dpr", lambda **kw: dcc.DatePickerRange(id="dpr", **kw)),
    "Graph": ("graph", lambda **kw: dcc.Graph(id="graph", **kw)),
    "Interval": ("intv", lambda **kw: dcc.Interval(id="intv", **kw)),
    "Input": ("inp", lambda **kw: dcc.Input(id="inp", **kw)),
    "Textarea": ("ta", lambda **kw: dcc.Textarea(id="ta", **kw)),
    "Tabs": ("tabs", lambda **kw: dcc.Tabs(id="tabs", **kw)),
    "Dropdown": ("dd", lambda **kw: dcc.Dropdown(id="dd", **kw)),
    "RadioItems": ("ri", lambda **kw: dcc.RadioItems(id="ri", **kw)),
    "Checklist": ("cl", lambda **kw: dcc.Checklist(id="cl", **kw)),
    "Store": ("store", lambda **kw: dcc.Store(id="store", **kw)),
    "Upload": ("upload", lambda **kw: dcc.Upload(id="upload", **kw)),
    "Slider": ("sl", lambda **kw: dcc.Slider(id="sl", **kw)),
    "RangeSlider": ("rs", lambda **kw: dcc.RangeSlider(id="rs", **kw)),
}


def _get_schema(component_type, prop):
    cid, factory = _COMPONENTS[component_type]
    app = _app_with_callback(factory(), input_prop=prop)
    tool = _user_tool(_tools_list(app))
    return _schema_for(tool)


# ---------------------------------------------------------------------------
# Static overrides — each override is tested independently
# ---------------------------------------------------------------------------


class TestStaticOverrides:
    """Props with explicit override schemas in component_schemas_overrides."""

    @pytest.mark.parametrize(
        "key,expected",
        list(OVERRIDE_SCHEMAS.items()),
        ids=[f"{c}.{p}" for c, p in OVERRIDE_SCHEMAS],
    )
    def test_override(self, key, expected):
        component_type, prop = key
        assert _get_schema(component_type, prop) == expected


# ---------------------------------------------------------------------------
# Introspection — representative samples (not exhaustive per-component)
# ---------------------------------------------------------------------------

INTROSPECTION_CASES = [
    # (component_type, prop, expected_schema) — one per distinct type shape
    (
        "Input",
        "value",
        {"anyOf": [{"type": "string"}, {"type": "number"}, {"type": "null"}]},
    ),
    (
        "Input",
        "disabled",
        {
            "anyOf": [
                {"type": "boolean"},
                {"const": "disabled", "type": "string"},
                {"const": "DISABLED", "type": "string"},
                {"type": "null"},
            ]
        },
    ),
    ("Input", "n_submit", {"anyOf": [{"type": "number"}, {"type": "null"}]}),
    (
        "Dropdown",
        "value",
        {
            "anyOf": [
                {"type": "string"},
                {"type": "number"},
                {"type": "boolean"},
                {
                    "items": {
                        "anyOf": [
                            {"type": "string"},
                            {"type": "number"},
                            {"type": "boolean"},
                        ]
                    },
                    "type": "array",
                },
                {"type": "null"},
            ]
        },
    ),
    ("Dropdown", "options", {"anyOf": [{}, {"type": "null"}]}),
    (
        "Checklist",
        "value",
        {
            "anyOf": [
                {
                    "items": {
                        "anyOf": [
                            {"type": "string"},
                            {"type": "number"},
                            {"type": "boolean"},
                        ]
                    },
                    "type": "array",
                },
                {"type": "null"},
            ]
        },
    ),
    (
        "Store",
        "data",
        {
            "anyOf": [
                {"additionalProperties": True, "type": "object"},
                {"items": {}, "type": "array"},
                {"type": "number"},
                {"type": "string"},
                {"type": "boolean"},
                {"type": "null"},
            ]
        },
    ),
    (
        "Upload",
        "contents",
        {
            "anyOf": [
                {"type": "string"},
                {"items": {"type": "string"}, "type": "array"},
                {"type": "null"},
            ]
        },
    ),
    (
        "RangeSlider",
        "value",
        {"anyOf": [{"items": {"type": "number"}, "type": "array"}, {"type": "null"}]},
    ),
    ("Tabs", "value", {"anyOf": [{"type": "string"}, {"type": "null"}]}),
]


class TestIntrospection:
    """Representative introspection tests — full type coverage in test_json_prop_typing."""

    @pytest.mark.parametrize(
        "component_type,prop,expected",
        INTROSPECTION_CASES,
        ids=[f"{c}.{p}" for c, p, _ in INTROSPECTION_CASES],
    )
    def test_introspected_schema(self, component_type, prop, expected):
        assert _get_schema(component_type, prop) == expected


# ---------------------------------------------------------------------------
# Callback annotation overrides
# ---------------------------------------------------------------------------


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


ANNOTATION_CASES = [
    (str, "disabled", {"type": "string"}),
    (int, "value", {"type": "integer"}),
    (float, "value", {"type": "number"}),
    (bool, "value", {"type": "boolean"}),
    (list, "value", {"items": {}, "type": "array"}),
    (dict, "value", {"additionalProperties": True, "type": "object"}),
    (Optional[int], "value", {"anyOf": [{"type": "integer"}, {"type": "null"}]}),
    (Optional[str], "value", {"anyOf": [{"type": "string"}, {"type": "null"}]}),
]


class TestAnnotationOverrides:
    """Callback type annotations override component schemas."""

    @pytest.mark.parametrize(
        "ann,prop,expected",
        ANNOTATION_CASES,
        ids=[
            f"{a.__name__ if hasattr(a, '__name__') else a}-{p}"
            for a, p, _ in ANNOTATION_CASES
        ],
    )
    def test_annotation(self, ann, prop, expected):
        app = _app_with_annotated_callback(ann, input_prop=prop)
        tool = _user_tool(_tools_list(app))
        assert _schema_for(tool, "val") == expected

    def test_no_annotation_uses_introspection(self):
        app = _app_with_annotated_callback(None)
        tool = _user_tool(_tools_list(app))
        assert _schema_for(tool, "val") == {
            "anyOf": [
                {"type": "boolean"},
                {"const": "disabled", "type": "string"},
                {"const": "DISABLED", "type": "string"},
                {"type": "null"},
            ]
        }


class TestAnnotationNullability:
    """Annotations control nullable vs non-nullable schemas."""

    def test_str_removes_null(self):
        app = Dash(__name__)
        app.layout = html.Div([dcc.Dropdown(id="dd"), html.Div(id="out")])

        @app.callback(Output("out", "children"), Input("dd", "value"))
        def update(val: str):
            return val

        tool = _user_tool(_tools_list(app))
        assert _schema_for(tool, "val") == {"type": "string"}

    def test_optional_preserves_null(self):
        app = Dash(__name__)
        app.layout = html.Div([dcc.Dropdown(id="dd"), html.Div(id="out")])

        @app.callback(Output("out", "children"), Input("dd", "value"))
        def update(val: Optional[str]):
            return val or ""

        tool = _user_tool(_tools_list(app))
        assert _schema_for(tool, "val") == {
            "anyOf": [{"type": "string"}, {"type": "null"}]
        }

    def test_optional_param_not_required(self):
        app = Dash(__name__)
        app.layout = html.Div([dcc.Dropdown(id="dd"), html.Div(id="out")])

        @app.callback(Output("out", "children"), Input("dd", "value"))
        def update(val: Optional[str]):
            return val or ""

        tool = _user_tool(_tools_list(app))
        assert "val" not in tool["inputSchema"].get("required", [])


class TestAnnotationWithState:
    """Annotations work for State parameters too."""

    def test_state_annotation_overrides(self):
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
        assert _schema_for(tool, "val") == {"type": "string"}
        assert _schema_for(tool, "data") == {
            "additionalProperties": True,
            "type": "object",
        }

    def test_partial_annotations(self):
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
        assert _schema_for(tool, "val") == {"type": "integer"}
        assert _schema_for(tool, "data") == {
            "anyOf": [
                {"additionalProperties": True, "type": "object"},
                {"items": {}, "type": "array"},
                {"type": "number"},
                {"type": "string"},
                {"type": "boolean"},
                {"type": "null"},
            ]
        }
