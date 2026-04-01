"""Description tests — verifies per-property description generation.

Tests are organized by description source:
- Labels (htmlFor, containment, text extraction)
- Component-specific (date pickers, sliders)
- Options (Dropdown, RadioItems, Checklist)
- Generic props (placeholder, default value, min/max/step)
- Chained callbacks (dynamic prop/options detection)
- Combinations (label + component-specific)
"""

import pytest

from dash import Dash, Input, Output, dcc, html

from tests.unit.mcp.conftest import (
    _app_with_callback,
    _desc_for,
    _tools_list,
    _user_tool,
)


def _app_with_layout(layout, *inputs):
    app = Dash(__name__)
    app.layout = layout

    @app.callback(
        Output("out", "children"),
        [Input(cid, prop) for cid, prop in inputs],
    )
    def update(*args):
        return str(args)

    return app


def _tool_for(component, input_prop="value"):
    app = _app_with_callback(component, input_prop=input_prop)
    return _user_tool(_tools_list(app))


# ---------------------------------------------------------------------------
# Labels
# ---------------------------------------------------------------------------


class TestLabels:
    def test_html_for(self):
        app = _app_with_layout(
            html.Div(
                [
                    html.Label("Your Name", htmlFor="inp"),
                    dcc.Input(id="inp"),
                    html.Div(id="out"),
                ]
            ),
            ("inp", "value"),
        )
        tool = _user_tool(_tools_list(app))
        assert "Your Name" in _desc_for(tool)

    def test_html_for_not_adjacent(self):
        app = _app_with_layout(
            html.Div(
                [
                    html.Div(html.Label("Remote Label", htmlFor="inp")),
                    dcc.Input(id="inp"),
                    html.Div(id="out"),
                ]
            ),
            ("inp", "value"),
        )
        tool = _user_tool(_tools_list(app))
        assert "Remote Label" in _desc_for(tool)

    def test_containment(self):
        app = _app_with_layout(
            html.Div(
                [
                    html.Label(
                        [
                            "Pick a city",
                            dcc.Dropdown(id="city_dd", options=["NYC", "LA"]),
                        ]
                    ),
                    html.Div(id="out"),
                ]
            ),
            ("city_dd", "value"),
        )
        tool = _user_tool(_tools_list(app))
        assert "Pick a city" in _desc_for(tool)

    def test_deeply_nested_containment(self):
        app = _app_with_layout(
            html.Div(
                [
                    html.Label(
                        [
                            html.Span("Nested Label"),
                            html.Div(dcc.Input(id="nested_inp")),
                        ]
                    ),
                    html.Div(id="out"),
                ]
            ),
            ("nested_inp", "value"),
        )
        tool = _user_tool(_tools_list(app))
        assert "Nested Label" in _desc_for(tool)

    def test_both_htmlfor_and_containment_captured(self):
        app = _app_with_layout(
            html.Div(
                [
                    html.Label(["Containment Label", dcc.Input(id="inp")]),
                    html.Label("HtmlFor Label", htmlFor="inp"),
                    html.Div(id="out"),
                ]
            ),
            ("inp", "value"),
        )
        tool = _user_tool(_tools_list(app))
        desc = _desc_for(tool)
        assert "HtmlFor Label" in desc
        assert "Containment Label" in desc

    def test_deep_text_extraction(self):
        app = _app_with_layout(
            html.Div(
                [
                    html.Label(
                        html.Div(html.Span(html.B("Deep Text"))),
                        htmlFor="inp",
                    ),
                    dcc.Input(id="inp"),
                    html.Div(id="out"),
                ]
            ),
            ("inp", "value"),
        )
        tool = _user_tool(_tools_list(app))
        assert "Deep Text" in _desc_for(tool)

    def test_multiple_text_nodes(self):
        app = _app_with_layout(
            html.Div(
                [
                    html.Label(
                        [html.B("First"), " ", html.I("Second")],
                        htmlFor="inp",
                    ),
                    dcc.Input(id="inp"),
                    html.Div(id="out"),
                ]
            ),
            ("inp", "value"),
        )
        tool = _user_tool(_tools_list(app))
        desc = _desc_for(tool)
        assert "Labeled with: First Second" in desc

    def test_unrelated_label_excluded(self):
        app = _app_with_layout(
            html.Div(
                [
                    html.Label("Other Field", htmlFor="other"),
                    dcc.Input(id="other"),
                    dcc.Input(id="target"),
                    html.Div(id="out"),
                ]
            ),
            ("target", "value"),
        )
        tool = _user_tool(_tools_list(app))
        desc = _desc_for(tool)
        assert "Other Field" not in (desc or "")


# ---------------------------------------------------------------------------
# Component-specific: date pickers
# ---------------------------------------------------------------------------


class TestDatePickerDescriptions:
    def test_single_full_range(self):
        dp = dcc.DatePickerSingle(
            id="dp",
            min_date_allowed="2020-01-01",
            max_date_allowed="2025-12-31",
        )
        desc = _desc_for(_tool_for(dp, "date"), "val")
        assert "2020-01-01" in desc
        assert "2025-12-31" in desc

    def test_single_min_only(self):
        dp = dcc.DatePickerSingle(id="dp", min_date_allowed="2020-01-01")
        desc = _desc_for(_tool_for(dp, "date"), "val")
        assert "min_date_allowed: '2020-01-01'" in desc

    def test_single_default_date(self):
        dp = dcc.DatePickerSingle(id="dp", date="2024-06-15")
        desc = _desc_for(_tool_for(dp, "date"), "val")
        assert "date: '2024-06-15'" in desc

    def test_range_with_constraints(self):
        dpr = dcc.DatePickerRange(
            id="dpr",
            min_date_allowed="2020-01-01",
            max_date_allowed="2025-12-31",
        )
        desc = _desc_for(_tool_for(dpr, "start_date"), "val")
        assert "2020-01-01" in desc


# ---------------------------------------------------------------------------
# Component-specific: sliders
# ---------------------------------------------------------------------------


class TestSliderDescriptions:
    def test_min_max(self):
        sl = dcc.Slider(id="sl", min=0, max=100)
        desc = _desc_for(_tool_for(sl), "val")
        assert "min: 0" in desc
        assert "max: 100" in desc

    def test_step(self):
        sl = dcc.Slider(id="sl", min=0, max=100, step=5)
        desc = _desc_for(_tool_for(sl), "val")
        assert "step: 5" in desc

    def test_default_value(self):
        sl = dcc.Slider(id="sl", min=0, max=100, value=50)
        desc = _desc_for(_tool_for(sl), "val")
        assert "value: 50" in desc

    def test_marks(self):
        sl = dcc.Slider(id="sl", min=0, max=100, marks={0: "Low", 100: "High"})
        desc = _desc_for(_tool_for(sl), "val")
        assert "marks: {0: 'Low', 100: 'High'}" in desc

    def test_range_slider_min_max(self):
        rs = dcc.RangeSlider(id="rs", min=0, max=100)
        desc = _desc_for(_tool_for(rs), "val")
        assert "min: 0" in desc
        assert "max: 100" in desc


# ---------------------------------------------------------------------------
# Options (parametrized across Dropdown, RadioItems, Checklist)
# ---------------------------------------------------------------------------


_OPTIONS_COMPONENTS = [
    ("Dropdown", lambda **kw: dcc.Dropdown(id="comp", **kw), "comp"),
    ("RadioItems", lambda **kw: dcc.RadioItems(id="comp", **kw), "comp"),
    ("Checklist", lambda **kw: dcc.Checklist(id="comp", **kw), "comp"),
]


class TestOptionsDescriptions:
    @pytest.mark.parametrize(
        "name,factory,cid", _OPTIONS_COMPONENTS, ids=[c[0] for c in _OPTIONS_COMPONENTS]
    )
    def test_options_shown(self, name, factory, cid):
        comp = factory(options=["X", "Y", "Z"])
        desc = _desc_for(_tool_for(comp), "val")
        assert "options: ['X', 'Y', 'Z']" in desc

    @pytest.mark.parametrize(
        "name,factory,cid", _OPTIONS_COMPONENTS, ids=[c[0] for c in _OPTIONS_COMPONENTS]
    )
    def test_default_shown(self, name, factory, cid):
        value = ["a"] if name == "Checklist" else "a"
        comp = factory(options=["a", "b"], value=value)
        desc = _desc_for(_tool_for(comp), "val")
        assert f"value: {value!r}" in desc

    def test_dropdown_dict_options(self):
        dd = dcc.Dropdown(
            id="dd",
            options=[
                {"label": "New York", "value": "NYC"},
            ],
        )
        assert "NYC" in _desc_for(_tool_for(dd), "val")

    def test_store_storage_type_template(self):
        store = dcc.Store(id="store", storage_type="session")
        app = _app_with_callback(store, input_prop="data")
        tool = _user_tool(_tools_list(app))
        desc = _desc_for(tool, "val")
        assert (
            "storage_type: 'session'. Describes how to store the value client-side"
            in desc
        )

    def test_many_options_truncated(self):
        dd = dcc.Dropdown(id="big", options=[str(i) for i in range(50)], value="0")
        app = _app_with_callback(dd)
        tool = _user_tool(_tools_list(app))
        desc = _desc_for(tool, "val")
        assert "options:" in desc
        assert "Use get_dash_component('big', 'options') for the full value" in desc


# ---------------------------------------------------------------------------
# Generic props
# ---------------------------------------------------------------------------


class TestGenericDescriptions:
    def test_placeholder(self):
        inp = dcc.Input(id="inp", placeholder="Enter your name")
        assert "placeholder: 'Enter your name'" in _desc_for(_tool_for(inp), "val")

    def test_numeric_min_max(self):
        inp = dcc.Input(id="inp", type="number", min=0, max=999)
        desc = _desc_for(_tool_for(inp), "val")
        assert "min: 0" in desc
        assert "max: 999" in desc

    def test_step(self):
        inp = dcc.Input(id="inp", type="number", min=0, max=100, step=0.1)
        assert "step: 0.1" in _desc_for(_tool_for(inp), "val")

    def test_default_value(self):
        inp = dcc.Input(id="inp", value="hello")
        desc = _desc_for(_tool_for(inp), "val")
        assert "value: 'hello'" in desc

    def test_non_text_type(self):
        inp = dcc.Input(id="inp", type="email")
        assert "type: 'email'" in _desc_for(_tool_for(inp), "val")

    def test_store_default(self):
        store = dcc.Store(id="store", data={"key": "value"})
        app = _app_with_callback(store, input_prop="data")
        tool = _user_tool(_tools_list(app))
        assert "data: {'key': 'value'}" in _desc_for(tool, "val")


# ---------------------------------------------------------------------------
# Chained callbacks
# ---------------------------------------------------------------------------


class TestChainedCallbacks:
    def test_options_set_by_upstream(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Dropdown(id="country", options=["US", "CA"], value="US"),
                dcc.Dropdown(id="city", options=[], value=None),
                html.Div(id="result"),
            ]
        )

        @app.callback(Output("city", "options"), Input("country", "value"))
        def update_cities(country):
            return ["NYC", "LA"] if country == "US" else ["Toronto"]

        @app.callback(Output("result", "children"), Input("city", "value"))
        def show_city(city):
            return city

        tools = _tools_list(app)
        tool = next(t for t in tools if "show_city" in t.name)
        desc = _desc_for(tool, "city")
        assert "can be updated by tool: `update_cities`" in desc
        assert "options:" in desc

    def test_value_set_by_upstream(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Input(id="source", value=""),
                html.Div(id="derived", children=""),
                html.Div(id="result"),
            ]
        )

        @app.callback(Output("derived", "children"), Input("source", "value"))
        def compute_derived(val):
            return f"derived: {val}"

        @app.callback(Output("result", "children"), Input("derived", "children"))
        def use_derived(val):
            return val

        tools = _tools_list(app)
        tool = next(t for t in tools if "use_derived" in t.name)
        desc = _desc_for(tool, "val")
        assert "can be updated by tool: `compute_derived`" in desc


# ---------------------------------------------------------------------------
# Combinations
# ---------------------------------------------------------------------------


class TestCombinations:
    def test_label_with_date_picker(self):
        dp = dcc.DatePickerSingle(
            id="dp",
            min_date_allowed="2020-01-01",
            max_date_allowed="2025-12-31",
        )
        app = _app_with_layout(
            html.Div(
                [
                    html.Label("Departure Date", htmlFor="dp"),
                    dp,
                    html.Div(id="out"),
                ]
            ),
            ("dp", "date"),
        )
        tool = _user_tool(_tools_list(app))
        desc = _desc_for(tool)
        assert "Departure Date" in desc
        assert "2020-01-01" in desc
