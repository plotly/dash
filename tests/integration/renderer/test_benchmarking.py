from dash import Dash, html, dcc, Input, Output, State, ALL, callback
import dash.testing.wait as wait
import time
import pytest


def make_app(num_groups=500, items_per_group=20):
    app = Dash(__name__)

    NUM_GROUPS = num_groups
    ITEMS_PER_GROUP = items_per_group

    children = []
    for g in range(NUM_GROUPS):
        group_children = []
        for i in range(ITEMS_PER_GROUP):
            group_children.append(
                html.Div(
                    [
                        dcc.Input(
                            id={"type": "input", "group": g, "index": i},
                            value=f"g{g}-i{i}",
                        ),
                        html.Div(
                            id={"type": "output", "group": g, "index": i},
                        ),
                    ]
                )
            )
        children.append(
            html.Details(
                [
                    html.Summary(f"Group {g}"),
                    html.Div(group_children),
                ]
            )
        )

    for g in range(NUM_GROUPS):

        @callback(
            Output({"type": "output", "group": g, "index": ALL}, "children"),
            Input({"type": "input", "group": g, "index": ALL}, "value"),
            prevent_initial_call=True,
        )
        def update(v, _g=g):
            return f"Updated: {v}"

    for g in range(NUM_GROUPS - 1):

        @callback(
            Output({"type": "output", "group": g + 1, "index": ALL}, "style"),
            Input({"type": "input", "group": g, "index": ALL}, "value"),
            prevent_initial_call=True,
        )
        def cross_update(values, _g=g):
            return [{"color": "blue"} for _ in values]

    for g in range(0, NUM_GROUPS, 3):

        @callback(
            Output({"type": "output", "group": g, "index": ALL}, "title"),
            Input({"type": "input", "group": g, "index": ALL}, "value"),
            State({"type": "output", "group": g, "index": ALL}, "children"),
            prevent_initial_call=True,
        )
        def tooltip_update(values, current, _g=g):
            return [f"{v} ({c})" for v, c in zip(values, current or [""] * len(values))]

    def layout():
        return html.Div(
            [
                html.H3("Dash 4 Firefox Performance MWE"),
                dcc.Input(id="input", value="initial value", type="text"),
                html.Div(id="output"),
                dcc.Store(id="store", data=time.time()),
                html.Div(children),
            ]
        )

    app.layout = layout

    app.clientside_callback(
        """
        function(value, ts) {
            if (!ts) return '';
            var now = Date.now() / 1000;
            return (now - ts).toFixed(2);
        }
        """,
        Output("output", "children"),
        Input("input", "value"),
        State("store", "data"),
    )

    return app


check_timing = {}


@pytest.mark.parametrize(
    "dev_tools,store",
    [
        ({"dev_tools_validate_callbacks": False}, "disabled"),
        ({"dev_tools_validate_callbacks": True}, "enabled"),
    ],
)
def test_compute_graph_timing(dash_duo, dev_tools, store):
    app = make_app()
    dash_duo.start_server(app, **dev_tools)
    times = []
    for _ in range(10):
        wait.until(
            lambda: dash_duo.find_element("#output").text.strip() != "", timeout=4
        )
        graph_compute_time = float(
            dash_duo.driver.execute_script(
                "return window.dash_clientside.callbackGraphTime"
            )
        )
        times.append(graph_compute_time)
        dash_duo.driver.refresh()
    avg_time = sum(times) / len(times) if times else 0
    check_timing[store] = avg_time
    if store == "enabled":
        print(f"Average time with store enabled: {avg_time:.2f} ms")
        assert (
            check_timing["disabled"] < avg_time
        ), "Expected faster performance with circular callback check disabled"
    if store == "disabled":
        print(f"Average time with store disabled: {avg_time:.2f} ms")
        assert (
            avg_time < 500
        ), "Expected average time to be under 1/2 seconds with circular callback check disabled"
