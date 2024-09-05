from multiprocessing import Value
import dash
from dash import Dash, html, dcc, Input, State, Output, ALL


def grouping_app():
    app = Dash(__name__)

    content = html.Div(
        [
            html.Div(id="title", children="Dash To-Do list"),
            dcc.Input(id="new-item"),
            html.Button("Add", id="add"),
            html.Div(id="list-container"),
            html.Hr(),
            html.Div(id="totals"),
            html.Hr(),
            html.Div(id="cc-args-grouping"),
            html.Div(id="cc-outputs-grouping"),
        ]
    )

    app.layout = html.Div([html.Div(id="content"), dcc.Location(id="url")])
    app.layout = content

    style_todo = {"display": "inline", "margin": "10px"}

    app.list_calls = Value("i", 0)
    app.style_calls = Value("i", 0)
    app.total_calls = Value("i", 0)

    @app.callback(
        dict(
            list_container=Output("list-container", "children"),
            new_item=Output("new-item", "value"),
            totals=Output("totals", "children"),
            cc_args_grouping=Output("cc-args-grouping", "children"),
            cc_outputs_grouping=Output("cc-outputs-grouping", "children"),
        ),
        dict(
            items=dict(
                all=State({"id": ALL}, "children"),
                new=State("new-item", "value"),
            ),
            triggers=[Input("add", "n_clicks"), Input("new-item", "n_submit")],
        ),
    )
    def edit_list(items, triggers):
        app.list_calls.value += 1
        triggered = [t["prop_id"] for t in dash.callback_context.triggered]
        adding = len(
            [1 for i in triggered if i in ("add.n_clicks", "new-item.n_submit")]
        )
        new_spec = items["all"]

        if adding:
            new_spec.append(items["new"])

        # Check callback context use of grouping
        assert dash.callback_context.using_args_grouping
        assert dash.callback_context.using_outputs_grouping

        new_list = [
            html.Div(
                [
                    dcc.Checklist(
                        id={"id": i, "property": "done"},
                        options=[{"label": "", "value": "done"}],
                        style={"display": "inline"},
                    ),
                    html.Div(text, id={"id": i}, style=style_todo),
                ],
                style={"clear": "both"},
            )
            for i, text in enumerate(new_spec)
        ]
        return {
            "list_container": new_list,
            "new_item": "",
            "totals": f"{len(new_list)} total item(s)",
            "cc_args_grouping": repr(dash.callback_context.args_grouping),
            "cc_outputs_grouping": repr(dash.callback_context.outputs_grouping),
        }

    return app
