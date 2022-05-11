import functools
import warnings
import json
from copy import deepcopy
import flask

from . import exceptions
from ._utils import stringify_id, AttributeDict


def has_context(func):
    @functools.wraps(func)
    def assert_context(*args, **kwargs):
        if not flask.has_request_context():
            raise exceptions.MissingCallbackContextException(
                f"dash.callback_context.{getattr(func, '__name__')} is only available from a callback!"
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
        """
        Returns a list of all the Input props that changed and caused the callback to execute. It is empty when the
        callback is called on initial load, unless an Input prop got its value from another initial callback.
        Callbacks triggered by user actions typically have one item in triggered, unless the same action changes
        two props at once or the callback has several Input props that are all modified by another callback based on
        a single user action.

        Example:  To get the id of the component that triggered the callback:
        `component_id = ctx.triggered[0]['prop_id'].split('.')[0]`

        Example:  To detect initial call, empty triggered is not really empty, it's falsy so that you can use:
        `if ctx.triggered:`
        """
        # For backward compatibility: previously `triggered` always had a
        # value - to avoid breaking existing apps, add a dummy item but
        # make the list still look falsy. So `if ctx.triggered` will make it
        # look empty, but you can still do `triggered[0]["prop_id"].split(".")`
        return getattr(flask.g, "triggered_inputs", []) or falsy_triggered

    @property
    @has_context
    def triggered_prop_ids(self):
        """
        Returns a dictionary of all the Input props that changed and caused the callback to execute. It is empty when
        the callback is called on initial load, unless an Input prop got its value from another initial callback.
        Callbacks triggered by user actions typically have one item in triggered, unless the same action changes
        two props at once or the callback has several Input props that are all modified by another callback based
        on a single user action.

        triggered_prop_ids (dict):
        - keys (str) : the triggered "prop_id" composed of "component_id.component_property"
        - values (str or dict): the id of the component that triggered the callback. Will be the dict id for pattern matching callbacks

        Example - regular callback
        {"btn-1.n_clicks": "btn-1"}

        Example - pattern matching callbacks:
        {'{"index":0,"type":"filter-dropdown"}.value': {"index":0,"type":"filter-dropdown"}}

        Example usage:
        `if "btn-1.n_clicks" in ctx.triggered_prop_ids:
            do_something()`
        """
        triggered = getattr(flask.g, "triggered_inputs", [])
        ids = AttributeDict({})
        for item in triggered:
            component_id, _, _ = item["prop_id"].rpartition(".")
            ids[item["prop_id"]] = component_id
            if component_id.startswith("{"):
                ids[item["prop_id"]] = AttributeDict(json.loads(component_id))
        return ids

    @property
    @has_context
    def triggered_id(self):
        """
        Returns the component id (str or dict) of the Input component that triggered the callback.

        Note - use `triggered_prop_ids` if you need both the component id and the prop that triggered the callback or if
        multiple Inputs triggered the callback.

        Example usage:
        `if "btn-1" == ctx.triggered_id:
            do_something()`

        """
        component_id = None
        if self.triggered:
            prop_id = self.triggered_prop_ids.first()
            component_id = self.triggered_prop_ids[prop_id]
        return component_id

    @property
    @has_context
    def args_grouping(self):
        """
        args_grouping is a dict of the inputs used with flexible callback signatures. The keys are the variable names
        and the values are dictionaries containing:
        - “id”: (string or dict) the component id. If it’s a pattern matching id, it will be a dict.
        - “id_str”: (str) for pattern matching ids, it’s the strigified dict id with no white spaces.
        - “property”: (str) The component property used in the callback.
        - “value”: the value of the component property at the time the callback was fired.
        - “triggered”: (bool)Whether this input triggered the callback.

        Example usage:
        @app.callback(
            Output("container", "children"),
            inputs=dict(btn1=Input("btn-1", "n_clicks"), btn2=Input("btn-2", "n_clicks")),
        )
        def display(btn1, btn2):
            c = ctx.args_grouping
            if c.btn1.triggered:
                return f"Button 1 clicked {btn1} times"
            elif c.btn2.triggered:
                return f"Button 2 clicked {btn2} times"
            else:
               return "No clicks yet"

        """
        triggered = getattr(flask.g, "triggered_inputs", [])
        triggered = [item["prop_id"] for item in triggered]
        grouping = getattr(flask.g, "args_grouping", {})

        def update_args_grouping(g):
            if isinstance(g, dict) and "id" in g:
                str_id = stringify_id(g["id"])
                prop_id = f"{str_id}.{g['property']}"

                new_values = {
                    "value": g.get("value"),
                    "str_id": str_id,
                    "triggered": prop_id in triggered,
                    "id": AttributeDict(g["id"])
                    if isinstance(g["id"], dict)
                    else g["id"],
                }
                g.update(new_values)

        def recursive_update(g):
            if isinstance(g, (tuple, list)):
                for i in g:
                    update_args_grouping(i)
                    recursive_update(i)
            if isinstance(g, dict):
                for i in g.values():
                    update_args_grouping(i)
                    recursive_update(i)

        recursive_update(grouping)

        return grouping

    # todo not sure whether we need this, but it removes a level of nesting so
    #  you don't need to use `.value` to get the value.
    @property
    @has_context
    def args_grouping_values(self):
        grouping = getattr(flask.g, "args_grouping", {})
        grouping = deepcopy(grouping)

        def recursive_update(g):
            if isinstance(g, (tuple, list)):
                for i in g:
                    recursive_update(i)
            if isinstance(g, dict):
                for k, v in g.items():
                    if isinstance(v, dict) and "id" in v:
                        g[k] = v["value"]
                    recursive_update(v)

        recursive_update(grouping)
        return grouping

    @property
    @has_context
    def outputs_grouping(self):
        return getattr(flask.g, "outputs_grouping", [])

    @property
    @has_context
    def outputs_list(self):
        if self.using_outputs_grouping:
            warnings.warn(
                "outputs_list is deprecated, use outputs_grouping instead",
                DeprecationWarning,
            )

        return getattr(flask.g, "outputs_list", [])

    @property
    @has_context
    def inputs_list(self):
        if self.using_args_grouping:
            warnings.warn(
                "inputs_list is deprecated, use args_grouping instead",
                DeprecationWarning,
            )

        return getattr(flask.g, "inputs_list", [])

    @property
    @has_context
    def states_list(self):
        if self.using_args_grouping:
            warnings.warn(
                "states_list is deprecated, use args_grouping instead",
                DeprecationWarning,
            )
        return getattr(flask.g, "states_list", [])

    @property
    @has_context
    def response(self):
        return getattr(flask.g, "dash_response")

    @staticmethod
    @has_context
    def record_timing(name, duration=None, description=None):
        """Records timing information for a server resource.

        :param name: The name of the resource.
        :type name: string

        :param duration: The time in seconds to report. Internally, this
            is rounded to the nearest millisecond.
        :type duration: float or None

        :param description: A description of the resource.
        :type description: string or None
        """
        timing_information = getattr(flask.g, "timing_information", {})

        if name in timing_information:
            raise KeyError(f'Duplicate resource name "{name}" found.')

        timing_information[name] = {"dur": round(duration * 1000), "desc": description}

        setattr(flask.g, "timing_information", timing_information)

    @property
    @has_context
    def using_args_grouping(self):
        """
        Return True if this callback is using dictionary or nested groupings for
        Input/State dependencies, or if Input and State dependencies are interleaved
        """
        return getattr(flask.g, "using_args_grouping", [])

    @property
    @has_context
    def using_outputs_grouping(self):
        """
        Return True if this callback is using dictionary or nested groupings for
        Output dependencies.
        """
        return getattr(flask.g, "using_outputs_grouping", [])


callback_context = CallbackContext()
