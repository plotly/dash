import functools
import flask

from . import exceptions


def has_context(func):
    @functools.wraps(func)
    def assert_context(*args, **kwargs):
        if not flask.has_request_context():
            raise exceptions.MissingCallbackContextException(
                'dash.callback.{} is only available from a callback!'.format(
                    getattr(func, '__name__')
                )
            )
        return func(*args, **kwargs)
    return assert_context


# pylint: disable=no-init
class CallbackContext:
    @property
    @has_context
    def inputs(self):
        return getattr(flask.g, 'input_values', {})

    @property
    @has_context
    def states(self):
        return getattr(flask.g, 'state_values', {})

    @property
    @has_context
    def triggered(self):
        return getattr(flask.g, 'triggered_inputs', [])
