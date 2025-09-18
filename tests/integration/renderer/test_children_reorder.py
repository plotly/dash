from dash import Dash, Input, Output, html, dcc, State, ALL


class Section:
    def __init__(self, idx):
        self.idx = idx
        self.options = ["A", "B", "C"]

    @property
    def section_id(self):
        return {"type": "section-container", "id": self.idx}

    @property
    def dropdown_id(self):
        return {"type": "dropdown", "id": self.idx}

    @property
    def swap_btn_id(self):
        return {"type": "swap-btn", "id": self.idx}

    def get_layout(self) -> html.Div:
        layout = html.Div(
            id=self.section_id,
            children=[
                html.H1(f"I am section {self.idx}"),
                html.Button(
                    "SWAP",
                    id=self.swap_btn_id,
                    n_clicks=0,
                    className=f"swap_button_{self.idx}",
                ),
                dcc.Dropdown(
                    self.options,
                    id=self.dropdown_id,
                    multi=True,
                    value=[],
                    className=f"dropdown_{self.idx}",
                ),
            ],
        )
        return layout


def test_roc001_reorder_children(dash_duo):
    app = Dash()

    app.layout = html.Div(
        id="main-app", children=[*[Section(idx=i).get_layout() for i in range(2)]]
    )

    @app.callback(
        Output("main-app", "children"),
        Input({"type": "swap-btn", "id": ALL}, "n_clicks"),
        State("main-app", "children"),
        prevent_initial_call=True,
    )
    def swap_button_action(n_clicks, children):
        if any(n > 0 for n in n_clicks):
            return children[::-1]

    dash_duo.start_server(app)

    for i in range(2):
        dash_duo.wait_for_text_to_equal("h1", f"I am section {i}")
        # dash_duo.wait_for_text_to_equal(
        #     f".dropdown_{i} .Select-multi-value-wrapper", "Select..."
        # )
        dash_duo.find_element(f".dropdown_{i}").click()
        dash_duo.find_element(
            f".dropdown_{i} .dash-dropdown-option:nth-child(1)"
        ).click()
        dash_duo.wait_for_text_to_equal(f".dropdown_{i} .dash-dropdown-trigger", "A")
        dash_duo.find_element(
            f".dropdown_{i} .dash-dropdown-option:nth-child(2)"
        ).click()
        dash_duo.wait_for_text_to_equal(
            f".dropdown_{i} .dash-dropdown-trigger", "A, B\n2 selected"
        )
        dash_duo.find_element(
            f".dropdown_{i} .dash-dropdown-option:nth-child(3)"
        ).click()
        dash_duo.wait_for_text_to_equal(
            f".dropdown_{i} .dash-dropdown-trigger", "A, B, C\n3 selected"
        )
        dash_duo.find_element(f".swap_button_{i}").click()
    dash_duo.wait_for_text_to_equal(
        f".dropdown_{0} .dash-dropdown-trigger", "A, B, C\n3 selected"
    )
    dash_duo.wait_for_text_to_equal(
        f".dropdown_{1} .dash-dropdown-trigger", "A, B, C\n3 selected"
    )
