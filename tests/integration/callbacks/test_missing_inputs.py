import json
from dash.testing import wait
from dash import Dash, Input, Output, State, ALL, MATCH, html


def wait_for_queue(dash_duo):
    # mostly for cases where no callbacks should fire:
    # just wait until we have the button and the queue is empty
    dash_duo.wait_for_text_to_equal("#btn", "click")
    wait.until(lambda: not dash_duo.redux_state_is_loading, 3)


def test_cbmi001_all_missing_inputs(dash_duo):
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.layout = html.Div(
        [
            html.Div("Title", id="title"),
            html.Button("click", id="btn"),
            html.Div(id="content"),
            html.Div("output1 init", id="out1"),
            html.Div("output2 init", id="out2"),
            html.Div("output3 init", id="out3"),
        ]
    )

    @app.callback(Output("content", "children"), [Input("btn", "n_clicks")])
    def content(n):
        return (
            [html.Div("A", id="a"), html.Div("B", id="b"), html.Div("C", id="c")]
            if n
            else "content init"
        )

    @app.callback(
        Output("out1", "children"),
        [Input("a", "children"), Input("b", "children")],
        [State("c", "children"), State("title", "children")],
    )
    def out1(a, b, c, title):
        # title exists at the start but State isn't enough to fire the callback
        assert c == "C"
        assert title == "Title"
        return a + b

    @app.callback(
        Output("out2", "children"),
        [Input("out1", "children")],
        [State("title", "children")],
    )
    def out2(out1, title):
        return out1 + " - 2 - " + title

    @app.callback(
        Output("out3", "children"),
        [Input("out1", "children"), Input("title", "children")],
    )
    def out3(out1, title):
        return out1 + " - 3 - " + title

    dash_duo.start_server(app)
    wait_for_queue(dash_duo)

    # out3 fires because it has another Input besides out1
    dash_duo.wait_for_text_to_equal("#out3", "output1 init - 3 - Title")

    assert dash_duo.find_element("#out1").text == "output1 init"

    # out2 doesn't fire because its only input (out1) is "prevented"
    # State items don't matter for this.
    assert dash_duo.find_element("#out2").text == "output2 init"

    dash_duo.find_element("#btn").click()

    # after a button click all inputs are present so all callbacks fire.
    dash_duo.wait_for_text_to_equal("#out1", "AB")
    dash_duo.wait_for_text_to_equal("#out2", "AB - 2 - Title")
    dash_duo.wait_for_text_to_equal("#out3", "AB - 3 - Title")

    assert not dash_duo.get_logs()


def test_cbmi002_follow_on_to_two_skipped_callbacks(dash_duo):
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.layout = html.Div(
        [
            html.Button("click", id="btn"),
            html.Div(id="content"),
            html.Div("output1 init", id="out1"),
            html.Div("output2 init", id="out2"),
            html.Div("output3 init", id="out3"),
        ]
    )

    @app.callback(Output("content", "children"), [Input("btn", "n_clicks")])
    def content(n):
        return [html.Div("A", id="a"), html.Div("B", id="b")] if n else "content init"

    @app.callback(Output("out1", "children"), [Input("a", "children")])
    def out1(a):
        return a

    @app.callback(Output("out2", "children"), [Input("b", "children")])
    def out2(b):
        return b

    @app.callback(
        Output("out3", "children"),
        [Input("out1", "children"), Input("out2", "children")],
    )
    def out3(out1, out2):
        return out1 + out2

    dash_duo.start_server(app)
    wait_for_queue(dash_duo)

    for i in ["1", "2", "3"]:
        assert dash_duo.find_element("#out" + i).text == "output{} init".format(i)

    dash_duo.find_element("#btn").click()
    # now all callbacks fire
    dash_duo.wait_for_text_to_equal("#out1", "A")
    dash_duo.wait_for_text_to_equal("#out2", "B")
    dash_duo.wait_for_text_to_equal("#out3", "AB")

    assert not dash_duo.get_logs()


def test_cbmi003_some_missing_inputs(dash_duo):
    # this one is an error!
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.layout = html.Div(
        [
            html.Div("Title", id="title"),
            html.Button("click", id="btn"),
            html.Div(id="content"),
            html.Div("output1 init", id="out1"),
            html.Div("output2 init", id="out2"),
        ]
    )

    @app.callback(Output("content", "children"), [Input("btn", "n_clicks")])
    def content(n):
        return [html.Div("A", id="a"), html.Div("B", id="b")] if n else "content init"

    @app.callback(
        Output("out1", "children"), [Input("a", "children"), Input("title", "children")]
    )
    def out1(a, title):
        return a + title

    @app.callback(Output("out2", "children"), [Input("out1", "children")])
    def out2(out1):
        return out1 + " - 2"

    dash_duo.start_server(app)
    wait_for_queue(dash_duo)

    dash_duo.wait_for_text_to_equal("#content", "content init")

    logs = json.dumps(dash_duo.get_logs())
    assert "ReferenceError" in logs
    assert "The id of this object is `a` and the property is `children`." in logs

    # after the error we can still use the app - and no more errors
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#out2", "ATitle - 2")
    assert not dash_duo.get_logs()


def test_cbmi004_some_missing_outputs(dash_duo):
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.layout = html.Div(
        [
            html.Button("click", id="btn"),
            html.Div(id="content"),
            html.Div("output1 init", id="out1"),
        ]
    )

    @app.callback(Output("content", "children"), [Input("btn", "n_clicks")])
    def content(n):
        return [html.Div("A", id="a"), html.Div("B", id="b")] if n else "content init"

    @app.callback(
        [Output("out1", "children"), Output("b", "children")], [Input("a", "children")]
    )
    def out1(a):
        return a, a

    dash_duo.start_server(app)
    wait_for_queue(dash_duo)

    dash_duo.wait_for_text_to_equal("#content", "content init")

    assert dash_duo.find_element("#out1").text == "output1 init"

    dash_duo.find_element("#btn").click()

    # after a button click all inputs are present so all callbacks fire.
    dash_duo.wait_for_text_to_equal("#out1", "A")
    dash_duo.wait_for_text_to_equal("#b", "A")

    assert not dash_duo.get_logs()


def test_cbmi005_all_multi_wildcards_with_output(dash_duo):
    # if all the inputs are multi wildcards, AND there's an output,
    # we DO fire the callback
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.layout = html.Div(
        [
            html.Div("Title", id="title"),
            html.Button("click", id="btn"),
            html.Div(id="content"),
            html.Div("output1 init", id="out1"),
            html.Div("output2 init", id="out2"),
        ]
    )

    @app.callback(Output("content", "children"), [Input("btn", "n_clicks")])
    def content(n):
        out = [html.Div("item {}".format(i), id={"i": i}) for i in range(n or 0)]
        return out or "content init"

    @app.callback(Output("out1", "children"), [Input({"i": ALL}, "children")])
    def out1(items):
        return ", ".join(items) or "no items"

    @app.callback(Output("out2", "children"), [Input("out1", "children")])
    def out2(out1):
        return out1 + " - 2"

    dash_duo.start_server(app)
    wait_for_queue(dash_duo)

    dash_duo.wait_for_text_to_equal("#out2", "no items - 2")

    assert dash_duo.find_element("#out1").text == "no items"
    assert dash_duo.find_element("#content").text == "content init"

    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#out1", "item 0")
    dash_duo.wait_for_text_to_equal("#out2", "item 0 - 2")

    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#out1", "item 0, item 1")
    dash_duo.wait_for_text_to_equal("#out2", "item 0, item 1 - 2")

    assert not dash_duo.get_logs()


def test_cbmi006_all_multi_wildcards_no_outputs(dash_duo):
    # if all the inputs are multi wildcards, but there's NO output,
    # we DO NOT fire the callback
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.layout = html.Div(
        [
            html.Div("Title", id="title"),
            html.Button("click", id="btn"),
            html.Div(id="content"),
            html.Div("output2 init", id="out2"),
        ]
    )

    @app.callback(Output("content", "children"), [Input("btn", "n_clicks")])
    def content(n):
        out = [html.Div("item {}".format(i), id={"i": i}) for i in range(n or 0)]
        return (out + [html.Div("output1 init", id="out1")]) if out else "content init"

    @app.callback(Output("out1", "children"), [Input({"i": ALL}, "children")])
    def out1(items):
        return ", ".join(items) or "no items"

    @app.callback(Output("out2", "children"), [Input("out1", "children")])
    def out2(out1):
        return out1 + " - 2"

    dash_duo.start_server(app)
    wait_for_queue(dash_duo)

    dash_duo.wait_for_text_to_equal("#out2", "output2 init")

    assert dash_duo.find_element("#content").text == "content init"

    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#out1", "item 0")
    dash_duo.wait_for_text_to_equal("#out2", "item 0 - 2")

    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#out1", "item 0, item 1")
    dash_duo.wait_for_text_to_equal("#out2", "item 0, item 1 - 2")

    assert not dash_duo.get_logs()


def test_cbmi007_all_multi_wildcards_some_outputs(dash_duo):
    # same as above (cbmi006) but multi-output, some outputs present some missing.
    # Again we DO NOT fire the callback
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.layout = html.Div(
        [
            html.Div("Title", id="title"),
            html.Button("click", id="btn"),
            html.Div(id="content"),
            html.Div("output2 init", id="out2"),
            html.Div("output3 init", id="out3"),
        ]
    )

    @app.callback(Output("content", "children"), [Input("btn", "n_clicks")])
    def content(n):
        out = [html.Div("item {}".format(i), id={"i": i}) for i in range(n or 0)]
        return (out + [html.Div("output1 init", id="out1")]) if out else "content init"

    @app.callback(
        [Output("out1", "children"), Output("out3", "children")],
        [Input({"i": ALL}, "children")],
    )
    def out1(items):
        out = ", ".join(items) or "no items"
        return out, (out + " - 3")

    @app.callback(Output("out2", "children"), [Input("out1", "children")])
    def out2(out1):
        return out1 + " - 2"

    dash_duo.start_server(app)
    wait_for_queue(dash_duo)

    dash_duo.wait_for_text_to_equal("#out2", "output2 init")
    dash_duo.wait_for_text_to_equal("#out3", "output3 init")

    assert dash_duo.find_element("#content").text == "content init"

    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#out1", "item 0")
    dash_duo.wait_for_text_to_equal("#out2", "item 0 - 2")
    dash_duo.wait_for_text_to_equal("#out3", "item 0 - 3")

    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#out1", "item 0, item 1")
    dash_duo.wait_for_text_to_equal("#out2", "item 0, item 1 - 2")
    dash_duo.wait_for_text_to_equal("#out3", "item 0, item 1 - 3")

    assert not dash_duo.get_logs()


def test_cbmi008_multi_wildcards_and_simple_all_missing(dash_duo):
    # if only SOME of the inputs are multi wildcards, even with an output,
    # we DO NOT fire the callback
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.layout = html.Div(
        [
            html.Div("Title", id="title"),
            html.Button("click", id="btn"),
            html.Div(id="content"),
            html.Div("output1 init", id="out1"),
            html.Div("output2 init", id="out2"),
        ]
    )

    @app.callback(Output("content", "children"), [Input("btn", "n_clicks")])
    def content(n):
        out = [html.Div("item {}".format(i), id={"i": i}) for i in range(n or 0)]
        return (out + [html.Div("A", id="a")]) if out else "content init"

    @app.callback(
        Output("out1", "children"),
        [Input({"i": ALL}, "children"), Input("a", "children")],
    )
    def out1(items, a):
        return a + " - " + (", ".join(items) or "no items")

    @app.callback(Output("out2", "children"), [Input("out1", "children")])
    def out2(out1):
        return out1 + " - 2"

    dash_duo.start_server(app)
    wait_for_queue(dash_duo)

    dash_duo.wait_for_text_to_equal("#content", "content init")

    assert dash_duo.find_element("#out1").text == "output1 init"
    assert dash_duo.find_element("#out2").text == "output2 init"

    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#out1", "A - item 0")
    dash_duo.wait_for_text_to_equal("#out2", "A - item 0 - 2")

    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#out1", "A - item 0, item 1")
    dash_duo.wait_for_text_to_equal("#out2", "A - item 0, item 1 - 2")

    assert not dash_duo.get_logs()


def test_cbmi009_match_wildcards_all_missing(dash_duo):
    # Kind of contrived - MATCH will always be 0. Just want to make sure
    # that this behaves the same as cbmi001
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.layout = html.Div(
        [
            html.Div("Title", id={"i": 0, "id": "title"}),
            html.Button("click", id="btn"),
            html.Div(id="content"),
            html.Div("output1 init", id={"i": 0, "id": "out1"}),
            html.Div("output2 init", id={"i": 0, "id": "out2"}),
            html.Div("output3 init", id={"i": 0, "id": "out3"}),
        ]
    )

    @app.callback(Output("content", "children"), [Input("btn", "n_clicks")])
    def content(n):
        return (
            [
                html.Div("A", id={"i": 0, "id": "a"}),
                html.Div("B", id={"i": 0, "id": "b"}),
                html.Div("C", id={"i": 0, "id": "c"}),
            ]
            if n
            else "content init"
        )

    @app.callback(
        Output({"i": MATCH, "id": "out1"}, "children"),
        [
            Input({"i": MATCH, "id": "a"}, "children"),
            Input({"i": MATCH, "id": "b"}, "children"),
        ],
        [
            State({"i": MATCH, "id": "c"}, "children"),
            State({"i": MATCH, "id": "title"}, "children"),
        ],
    )
    def out1(a, b, c, title):
        # title exists at the start but State isn't enough to fire the callback
        assert c == "C"
        assert title == "Title"
        return a + b

    @app.callback(
        Output({"i": MATCH, "id": "out2"}, "children"),
        [Input({"i": MATCH, "id": "out1"}, "children")],
        [State({"i": MATCH, "id": "title"}, "children")],
    )
    def out2(out1, title):
        return out1 + " - 2 - " + title

    @app.callback(
        Output({"i": MATCH, "id": "out3"}, "children"),
        [
            Input({"i": MATCH, "id": "out1"}, "children"),
            Input({"i": MATCH, "id": "title"}, "children"),
        ],
    )
    def out3(out1, title):
        return out1 + " - 3 - " + title

    dash_duo.start_server(app)
    wait_for_queue(dash_duo)

    def cssid(v):
        # escaped CSS for object IDs
        return r"#\{\"i\"\:0\,\"id\"\:\"" + v + r"\"\}"

    # out3 fires because it has another Input besides out1
    dash_duo.wait_for_text_to_equal(cssid("out3"), "output1 init - 3 - Title")

    assert dash_duo.find_element(cssid("out1")).text == "output1 init"

    # out2 doesn't fire because its only input (out1) is "prevented"
    # State items don't matter for this.
    assert dash_duo.find_element(cssid("out2")).text == "output2 init"

    dash_duo.find_element("#btn").click()

    # after a button click all inputs are present so all callbacks fire.
    dash_duo.wait_for_text_to_equal(cssid("out1"), "AB")
    dash_duo.wait_for_text_to_equal(cssid("out2"), "AB - 2 - Title")
    dash_duo.wait_for_text_to_equal(cssid("out3"), "AB - 3 - Title")

    assert not dash_duo.get_logs()
