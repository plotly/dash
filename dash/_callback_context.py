import functools
import flask

from . import exceptions


def has_context(func):
    @functools.wraps(func)
    def assert_context(*args, **kwargs):
        if not flask.has_request_context():
            raise exceptions.MissingCallbackContextException(
                ("dash.callback_context.{} is only available from a callback!").format(
                    getattr(func, "__name__")
                )
            )
        return func(*args, **kwargs)

    return assert_context


class FalsyList(list):
    def __bool__(self):
        # for Python 3
        return False

    def __nonzero__(self):
        # for Python 2
        return False


falsy_triggered = FalsyList([{"prop_id": ".", "value": None}])


# pylint: disable=no-init
class CallbackContext:
    @property
    @has_context
    def inputs(self):
        return getattr(flask.g, "input_values", {})

    @property
    @has_context
    def states(self):
        return getattr(flask.g, "state_values", {})

    @property
    @has_context
    def triggered(self):
        # For backward compatibility: previously `triggered` always had a
        # value - to avoid breaking existing apps, add a dummy item but
        # make the list still look falsy. So `if ctx.triggered` will make it
        # look empty, but you can still do `triggered[0]["prop_id"].split(".")`
        return getattr(flask.g, "triggered_inputs", []) or falsy_triggered

    @property
    @has_context
    def outputs_list(self):
        return getattr(flask.g, "outputs_list", [])

    @property
    @has_context
    def inputs_list(self):
        return getattr(flask.g, "inputs_list", [])

    @property
    @has_context
    def states_list(self):
        return getattr(flask.g, "states_list", [])

    @property
    @has_context
    def response(self):
        return getattr(flask.g, "dash_response")


callback_context = CallbackContext()
