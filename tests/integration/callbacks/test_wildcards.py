from multiprocessing import Value
import re

import dash_html_components as html
import dash_core_components as dcc
import dash
from dash.dependencies import Input, Output, State, ALL, ALLSMALLER, MATCH


def css_escape(s):
    sel = re.sub('[\\{\\}\\"\\\'.:,]', lambda m: '\\' + m.group(0), s)
    print(sel)
    return sel


def todo_app():
    app = dash.Dash(__name__)

    app.layout = html.Div([
        html.Div('Dash To-Do list'),
        dcc.Input(id="new-item"),
        html.Button("Add", id="add"),
        html.Button("Clear Done", id="clear-done"),
        html.Div(id="list-container"),
        html.Hr(),
        html.Div(id="totals")
    ])

    style_todo = {"display": "inline", "margin": "10px"}
    style_done = {"textDecoration": "line-through", "color": "#888"}
    style_done.update(style_todo)

    app.list_calls = Value('i', 0)
    app.style_calls = Value('i', 0)
    app.preceding_calls = Value('i', 0)
    app.total_calls = Value('i', 0)

    @app.callback(
        [
            Output("list-container", "children"),
            Output("new-item", "value")
        ],
        [
            Input("add", "n_clicks"),
            Input("new-item", "n_submit"),
            Input("clear-done", "n_clicks")
        ],
        [
            State("new-item", "value"),
            State({"item": ALL}, "children"),
            State({"item": ALL, "action": "done"}, "value")
        ]
    )
    def edit_list(add, add2, clear, new_item, items, items_done):
        app.list_calls.value += 1
        triggered = [t["prop_id"] for t in dash.callback_context.triggered]
        adding = len(
            [1 for i in triggered if i in ("add.n_clicks", "new-item.n_submit")]
        )
        clearing = len([1 for i in triggered if i == "clear-done.n_clicks"])
        new_spec = [
            (text, done) for text, done in zip(items, items_done)
            if not (clearing and done)
        ]
        if adding:
            new_spec.append((new_item, []))
        new_list = [
            html.Div([
                dcc.Checklist(
                    id={"item": i, "action": "done"},
                    options=[{"label": "", "value": "done"}],
                    value=done,
                    style={"display": "inline"}
                ),
                html.Div(
                    text,
                    id={"item": i},
                    style=style_done if done else style_todo
                ),
                html.Div(id={"item": i, "preceding": True}, style=style_todo)
            ], style={"clear": "both"})
            for i, (text, done) in enumerate(new_spec)
        ]
        return [new_list, "" if adding else new_item]

    @app.callback(
        Output({"item": MATCH}, "style"),
        [Input({"item": MATCH, "action": "done"}, "value")]
    )
    def mark_done(done):
        app.style_calls.value += 1
        return style_done if done else style_todo

    @app.callback(
        Output({"item": MATCH, "preceding": True}, "children"),
        [
            Input({"item": ALLSMALLER, "action": "done"}, "value"),
            Input({"item": MATCH, "action": "done"}, "value")
        ]
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
        Output("totals", "children"),
        [Input({"item": ALL, "action": "done"}, "value")]
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


def test_cbwc001_todo_app(dash_duo):
    app = todo_app()
    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#totals", "0 of 0 items completed")
    assert app.list_calls.value == 1
    assert app.style_calls.value == 0
    assert app.preceding_calls.value == 0
    assert app.total_calls.value == 1

    new_item = dash_duo.find_element("#new-item")
    add_item = dash_duo.find_element("#add")
    clear_done = dash_duo.find_element("#clear-done")

    def assert_count(items):
        assert len(dash_duo.find_elements("#list-container>div")) == items

    def get_done_item(item):
        selector = css_escape('#{"action":"done","item":%d} input' % item)
        return dash_duo.find_element(selector)

    def assert_item(item, text, done, prefix="", suffix=""):
        text_el = dash_duo.find_element(css_escape('#{"item":%d}' % item))
        assert text_el.text == text, "item {} text".format(item)

        note_el = dash_duo.find_element(
            css_escape('#{"item":%d,"preceding":true}' % item)
        )
        expected_note = "" if done else (prefix + " preceding items are done" + suffix)
        assert note_el.text == expected_note, "item {} note".format(item)

        assert bool(get_done_item(item).get_attribute('checked')) == done

    new_item.send_keys("apples")
    add_item.click()
    dash_duo.wait_for_text_to_equal("#totals", "0 of 1 items completed - 0%")
    assert_count(1)

    new_item.send_keys("bananas")
    add_item.click()
    dash_duo.wait_for_text_to_equal("#totals", "0 of 2 items completed - 0%")
    assert_count(2)

    new_item.send_keys("carrots")
    add_item.click()
    dash_duo.wait_for_text_to_equal("#totals", "0 of 3 items completed - 0%")
    assert_count(3)

    new_item.send_keys("dates")
    add_item.click()
    dash_duo.wait_for_text_to_equal("#totals", "0 of 4 items completed - 0%")
    assert_count(4)
    assert_item(0, "apples", False, "0 of 0", " DO THIS NEXT!")
    assert_item(1, "bananas", False, "0 of 1")
    assert_item(2, "carrots", False, "0 of 2")
    assert_item(3, "dates", False, "0 of 3")

    get_done_item(2).click()
    dash_duo.wait_for_text_to_equal("#totals", "1 of 4 items completed - 25%")
    assert_item(0, "apples", False, "0 of 0", " DO THIS NEXT!")
    assert_item(1, "bananas", False, "0 of 1")
    assert_item(2, "carrots", True)
    assert_item(3, "dates", False, "1 of 3")

    get_done_item(0).click()
    dash_duo.wait_for_text_to_equal("#totals", "2 of 4 items completed - 50%")
    assert_item(0, "apples", True)
    assert_item(1, "bananas", False, "1 of 1", " DO THIS NEXT!")
    assert_item(2, "carrots", True)
    assert_item(3, "dates", False, "2 of 3")

    clear_done.click()
    dash_duo.wait_for_text_to_equal("#totals", "0 of 2 items completed - 0%")
    assert_count(2)
    assert_item(0, "bananas", False, "0 of 0", " DO THIS NEXT!")
    assert_item(1, "dates", False, "0 of 1")

    get_done_item(0).click()
    dash_duo.wait_for_text_to_equal("#totals", "1 of 2 items completed - 50%")
    assert_item(0, "bananas", True)
    assert_item(1, "dates", False, "1 of 1", " DO THIS NEXT!")

    get_done_item(1).click()
    dash_duo.wait_for_text_to_equal("#totals", "2 of 2 items completed - 100%")
    assert_item(0, "bananas", True)
    assert_item(1, "dates", True)

    clear_done.click()
    # This was a tricky one - trigger based on deleted components
    dash_duo.wait_for_text_to_equal("#totals", "0 of 0 items completed")
    assert_count(0)
