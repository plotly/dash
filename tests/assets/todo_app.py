from multiprocessing import Value

import dash
from dash import html, dcc, Input, Output, State, MATCH, ALL, ALLSMALLER


def todo_app(content_callback=False):
    app = dash.Dash(__name__)

    content = html.Div(
        [
            html.Div("Dash To-Do list"),
            dcc.Input(id="new-item"),
            html.Button("Add", id="add"),
            html.Button("Clear Done", id="clear-done"),
            html.Div(id="list-container"),
            html.Hr(),
            html.Div(id="totals"),
        ]
    )

    if content_callback:
        app.layout = html.Div([html.Div(id="content"), dcc.Location(id="url")])

        @app.callback(Output("content", "children"), [Input("url", "pathname")])
        def display_content(_):
            return content

    else:
        app.layout = content

    style_todo = {"display": "inline", "margin": "10px"}
    style_done = {"textDecoration": "line-through", "color": "#888"}
    style_done.update(style_todo)

    app.list_calls = Value("i", 0)
    app.style_calls = Value("i", 0)
    app.preceding_calls = Value("i", 0)
    app.total_calls = Value("i", 0)

    @app.callback(
        Output("list-container", "children"),
        Output("new-item", "value"),
        Input("add", "n_clicks"),
        Input("new-item", "n_submit"),
        Input("clear-done", "n_clicks"),
        State("new-item", "value"),
        State({"item": ALL}, "children"),
        State({"item": ALL, "action": "done"}, "value"),
    )
    def edit_list(add, add2, clear, new_item, items, items_done):
        app.list_calls.value += 1
        triggered = [t["prop_id"] for t in dash.callback_context.triggered]
        adding = len(
            [1 for i in triggered if i in ("add.n_clicks", "new-item.n_submit")]
        )
        clearing = len([1 for i in triggered if i == "clear-done.n_clicks"])
        new_spec = [
            (text, done)
            for text, done in zip(items, items_done)
            if not (clearing and done)
        ]
        if adding:
            new_spec.append((new_item, []))

        # Check callback context use of grouping
        assert not dash.callback_context.using_args_grouping
        assert not dash.callback_context.using_outputs_grouping

        new_list = [
            html.Div(
                [
                    dcc.Checklist(
                        id={"item": i, "action": "done"},
                        options=[{"label": "", "value": "done"}],
                        value=done,
                        style={"display": "inline"},
                    ),
                    html.Div(
                        text, id={"item": i}, style=style_done if done else style_todo
                    ),
                    html.Div(id={"item": i, "preceding": True}, style=style_todo),
                ],
                style={"clear": "both"},
            )
            for i, (text, done) in enumerate(new_spec)
        ]
        return [new_list, "" if adding else new_item]

    @app.callback(
        Output({"item": MATCH}, "style"),
        Input({"item": MATCH, "action": "done"}, "value"),
    )
    def mark_done(done):
        app.style_calls.value += 1
        return style_done if done else style_todo

    @app.callback(
        Output({"item": MATCH, "preceding": True}, "children"),
        Input({"item": ALLSMALLER, "action": "done"}, "value"),
        Input({"item": MATCH, "action": "done"}, "value"),
    )
    def show_preceding(done_before, this_done):
        app.preceding_calls.value += 1
        if this_done:
            return ""
        all_before = len(done_before)
        done_before = len([1 for d in done_before if d])
        out = "{} of {} preceding items are done".format(done_before, all_before)
        if all_before == done_before:
            out += " DO THIS NEXT!"
        return out

    @app.callback(
        Output("totals", "children"), Input({"item": ALL, "action": "done"}, "value")
    )
    def show_totals(done):
        app.total_calls.value += 1
        count_all = len(done)
        count_done = len([d for d in done if d])
        result = "{} of {} items completed".format(count_done, count_all)
        if count_all:
            result += " - {}%".format(int(100 * count_done / count_all))
        return result

    return app
