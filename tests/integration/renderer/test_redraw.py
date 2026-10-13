import time
from dash import Dash, Input, Output, html, ctx, remount

import dash_test_components as dt


def test_rdraw001_redraw(dash_duo):
    app = Dash()

    app.layout = html.Div(
        [
            html.Div(
                dt.DrawCounter(id="counter"),
                id="redrawer",
            ),
            html.Button("redraw", id="redraw"),
        ]
    )

    @app.callback(
        Output("redrawer", "children"),
        Input("redraw", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_click(_):
        return dt.DrawCounter(id="counter")

    dash_duo.start_server(app)

    # The same component (same type & id) returned from a callback is
    # reconciled in place: it re-renders (counter increments) instead of
    # being unmounted & remounted (which would reset the counter to 1).
    dash_duo.wait_for_text_to_equal("#counter", "1")
    dash_duo.find_element("#redraw").click()
    dash_duo.wait_for_text_to_equal("#counter", "2")
    time.sleep(1)
    dash_duo.wait_for_text_to_equal("#counter", "2")


def test_rdraw002_remount_on_identity_change(dash_duo):
    # A *different* component (type change) at the same path must be
    # remounted, not reconciled: the counter resets on each swap back.
    app = Dash()

    app.layout = html.Div(
        [
            html.Div(
                dt.DrawCounter(id="counter"),
                id="redrawer",
            ),
            html.Button("redraw", id="redraw"),
        ]
    )

    @app.callback(
        Output("redrawer", "children"),
        Input("redraw", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_click(n):
        if n % 2:
            return html.Div("not a counter", id="counter")
        return dt.DrawCounter(id="counter")

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#counter", "1")
    dash_duo.find_element("#redraw").click()
    dash_duo.wait_for_text_to_equal("#counter", "not a counter")
    dash_duo.find_element("#redraw").click()
    # Fresh mount, not a third render of the original counter.
    dash_duo.wait_for_text_to_equal("#counter", "1")


def test_rdraw003_children_update_in_place(dash_duo):
    # Children returned from a callback with an unchanged structure must
    # update the existing DOM nodes in place, not unmount/remount the
    # whole subtree. Regression test for #3846.
    app = Dash()
    n_rows = 20

    app.layout = html.Div(
        [
            html.Button("Re-render", id="btn", n_clicks=0),
            html.Div(id="content"),
        ]
    )

    @app.callback(Output("content", "children"), Input("btn", "n_clicks"))
    def render(n):
        return [
            html.Div(
                [html.Span(f"Field {i}"), html.Span(f"value {i} @ click {n}")],
                className="row",
            )
            for i in range(n_rows)
        ]

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal(
        "#content .row:first-child span:last-child", "value 0 @ click 0"
    )

    # Tag every rendered element; remounted elements lose the tag.
    dash_duo.driver.execute_script(
        "document.querySelectorAll('#content *')"
        ".forEach(el => el.__dash_test_probe = true)"
    )
    n_elements = dash_duo.driver.execute_script(
        "return document.querySelectorAll('#content *').length"
    )
    assert n_elements == n_rows * 3

    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal(
        "#content .row:first-child span:last-child", "value 0 @ click 1"
    )

    reused = dash_duo.driver.execute_script(
        "return [...document.querySelectorAll('#content *')]"
        ".filter(el => el.__dash_test_probe).length"
    )
    assert reused == n_elements


def test_rdraw004_explicit_remount(dash_duo):
    # `dash.remount()` forces a remount (resetting internal state) even when
    # the component identity is unchanged, without having to change the id.
    # The same component returned plain reconciles in place (counter keeps
    # incrementing); wrapped in remount() it resets to 1.
    app = Dash()

    app.layout = html.Div(
        [
            html.Div(dt.DrawCounter(id="counter"), id="box"),
            html.Button("plain", id="plain"),
            html.Button("remount", id="remount"),
        ]
    )

    @app.callback(
        Output("box", "children"),
        Input("plain", "n_clicks"),
        Input("remount", "n_clicks"),
        prevent_initial_call=True,
    )
    def update(_plain, _remount):
        if ctx.triggered_id == "remount":
            return remount(dt.DrawCounter(id="counter"))
        return dt.DrawCounter(id="counter")

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#counter", "1")
    # Plain re-renders reconcile in place: the counter increments.
    dash_duo.find_element("#plain").click()
    dash_duo.wait_for_text_to_equal("#counter", "2")
    dash_duo.find_element("#plain").click()
    dash_duo.wait_for_text_to_equal("#counter", "3")
    # remount() resets internal state.
    dash_duo.find_element("#remount").click()
    dash_duo.wait_for_text_to_equal("#counter", "1")
    # ...and reconciliation resumes afterwards.
    dash_duo.find_element("#plain").click()
    dash_duo.wait_for_text_to_equal("#counter", "2")
    # remount() works repeatedly.
    dash_duo.find_element("#remount").click()
    dash_duo.wait_for_text_to_equal("#counter", "1")

    assert dash_duo.get_logs() == []
