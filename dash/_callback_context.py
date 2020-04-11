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
        return getattr(flask.g, "triggered_inputs", [])

    @property
    @has_context
    def response(self):
        return getattr(flask.g, "dash_response")

    @has_context
    def record_timing(self, name, duration=None, description=None):
        """Records timing information for a server resource.

        :param name: The name of the resource.
        :type name: string

        :param duration: The time in seconds to report. Internally, this
            is rounded to the nearest millisecond.
        :type duration: float or None

        :param description: A description of the resource.
        :type description: string or None
        """
        timing_information = getattr(flask.g, 'timing_information', {})

        if name in timing_information:
            raise KeyError('Duplicate resource name "{}" found.'.format(name))

        timing_information[name] = {
            'dur': round(duration*1000),
            'desc': description
        }

        setattr(flask.g, 'timing_information', timing_information)
