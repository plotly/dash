from dash import dcc, html, Input, Output, Patch, Dash


def test_dcl001_descendant_tabs(dash_duo):
    app = Dash()

    app.layout = html.Div(
        [
            html.Button("Enable Tabs", id="button", n_clicks=0),
            html.Button("Add Tabs", id="add_button", n_clicks=0),
            dcc.Store(id="store-data", data=None),
            dcc.Tabs(
                [
                    dcc.Tab(label="Tab A", value="tab-a", id="tab-a", disabled=True),
                    dcc.Tab(label="Tab B", value="tab-b", id="tab-b", disabled=True),
                ],
                id="tabs",
                value="tab-a",
            ),
        ]
    )

    @app.callback(Output("store-data", "data"), Input("button", "n_clicks"))
    def update_store_data(clicks):
        if clicks > 0:
            return {"data": "available"}
        return None

    @app.callback(
        Output("tabs", "children"),
        Input("add_button", "n_clicks"),
        prevent_initial_call=True,
    )
    def add_tabs(n):
        children = Patch()
        children.append(dcc.Tab(label=f"{n}", value=f"{n}", id=f"test-{n}"))
        return children

    @app.callback(
        Output("tab-a", "disabled"),
        Output("tab-b", "disabled"),
        Input("store-data", "data"),
    )
    def toggle_tabs(store_data):
        if store_data is not None and "data" in store_data:
            return False, False
        return True, True

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#button", "Enable Tabs")
    dash_duo.find_element("#tab-a.tab--disabled")
    dash_duo.find_element("#button").click()
    dash_duo.find_element("#tab-a:not(.tab--disabled)")
    dash_duo.find_element("#add_button").click()
    dash_duo.find_element("#test-1:not(.tab--disabled)")
