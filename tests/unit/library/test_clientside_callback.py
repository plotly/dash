import pytest

import dash
from dash import ClientsideFunction, Input, Output, State
from dash.exceptions import CallbackException


def make_app():
    app = dash.Dash()
    return app


def register(app, **kwargs):
    return app.clientside_callback(
        "function(value) { return value; }",
        Output("out", "children"),
        Input("in", "value"),
        **kwargs,
    )


@pytest.mark.parametrize(
    "kwarg",
    [
        {"background": True},
        {"interval": 500},
        {"progress": Output("p", "value")},
        {"progress_default": 0},
        {"cancel": Input("c", "n_clicks")},
        {"manager": object()},
        {"cache_args_to_ignore": [0]},
        {"cache_ignore_triggered": False},
        {"api_endpoint": "/api"},
        {"websocket": True},
        {"persistent": True},
        {"mcp_enabled": True},
        {"mcp_expose_docstring": True},
    ],
)
def test_clientside_rejects_serverside_only_kwargs(kwarg):
    app = make_app()
    with pytest.raises(CallbackException) as err:
        register(app, **kwarg)
    assert "only supported by server-side callbacks" in str(err.value)
    assert f"`{next(iter(kwarg))}`" in str(err.value)


def test_clientside_rejects_unknown_kwargs():
    app = make_app()
    with pytest.raises(CallbackException) as err:
        register(app, prevnt_initial_call=True)
    assert "unexpected keyword argument" in str(err.value)
    assert "`prevnt_initial_call`" in str(err.value)


def test_clientside_supported_kwargs_accepted():
    app = make_app()
    register(app, prevent_initial_call=True, hidden=True, optional=True)
    spec = app._callback_list[-1]
    assert spec["prevent_initial_call"] is True
    assert spec["hidden"] is True
    assert spec["optional"] is True


def test_clientside_running_spec():
    app = make_app()
    register(app, running=[(Output("btn", "disabled"), True, False)])
    assert app._callback_list[-1]["running"] == {
        "running": {"btn.disabled": True},
        "runningOff": {"btn.disabled": False},
    }


def test_clientside_running_single_tuple_spec():
    app = make_app()
    register(app, running=[Output("btn", "disabled"), True, False])
    assert app._callback_list[-1]["running"] == {
        "running": {"btn.disabled": True},
        "runningOff": {"btn.disabled": False},
    }


def test_clientside_on_error_inline_string():
    app = make_app()
    register(app, on_error="function(err) { return 'handled'; }")
    on_error = app._callback_list[-1]["clientside_on_error"]
    assert on_error["namespace"] == "_dashprivate_clientside_funcs"
    # The handler source is injected as an inline script under its hash name
    assert any(on_error["function_name"] in script for script in app._inline_scripts)


def test_clientside_on_error_clientside_function():
    app = make_app()
    register(app, on_error=ClientsideFunction("ns", "handler"))
    assert app._callback_list[-1]["clientside_on_error"] == {
        "namespace": "ns",
        "function_name": "handler",
    }


def test_clientside_on_error_rejects_python_callable():
    app = make_app()
    with pytest.raises(CallbackException) as err:
        register(app, on_error=lambda e: None)
    assert "JavaScript function" in str(err.value)


def test_clientside_no_on_error_key_by_default():
    app = make_app()
    register(app)
    assert "clientside_on_error" not in app._callback_list[-1]


def test_clientside_no_output_grouped_inputs():
    app = make_app()
    app.clientside_callback(
        "function({a}) { dash_clientside.set_props('x', {children: a}); }",
        inputs=dict(a=Input("in", "value")),
    )
    spec = app._callback_list[-1]
    assert spec["no_output"] is True
    assert spec["inputs_state_indices"] == dict(a=0)


def test_clientside_state_kwarg_grouping():
    app = make_app()
    app.clientside_callback(
        "function({a, s}) { return a + s; }",
        output=Output("out", "children"),
        inputs=dict(a=Input("in", "value")),
        state=dict(s=State("st", "value")),
    )
    spec = app._callback_list[-1]
    assert spec["inputs_state_indices"] == dict(a=0, s=1)
