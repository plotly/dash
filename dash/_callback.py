import collections
from functools import wraps

from .dependencies import (
    handle_callback_args,
    handle_grouped_callback_args,
    Output,
)
from .exceptions import PreventUpdate

from ._grouping import (
    flatten_grouping,
    make_grouping_by_index,
    grouping_len,
)
from ._utils import (
    create_callback_id,
    stringify_id,
    to_json,
)

from . import _validate


class NoUpdate:
    # pylint: disable=too-few-public-methods
    pass


GLOBAL_CALLBACK_LIST = []
GLOBAL_CALLBACK_MAP = {}
GLOBAL_INLINE_SCRIPTS = []


def callback(*_args, **_kwargs):
    """
    Normally used as a decorator, `@dash.callback` provides a server-side
    callback relating the values of one or more `Output` items to one or
    more `Input` items which will trigger the callback when they change,
    and optionally `State` items which provide additional information but
    do not trigger the callback directly.

    `@dash.callback` is an alternative to `@app.callback` (where `app = dash.Dash()`)
    introduced in Dash 2.0.
    It allows you to register callbacks without defining or importing the `app`
    object. The call signature is identical and it can be used instead of `app.callback`
    in all cases.

    The last, optional argument `prevent_initial_call` causes the callback
    not to fire when its outputs are first added to the page. Defaults to
    `False` and unlike `app.callback` is not configurable at the app level.
    """
    return register_callback(
        GLOBAL_CALLBACK_LIST,
        GLOBAL_CALLBACK_MAP,
        False,
        *_args,
        **_kwargs,
    )


def clientside_callback(clientside_function, *args, **kwargs):
    return register_clientside_callback(
        GLOBAL_CALLBACK_LIST,
        GLOBAL_CALLBACK_MAP,
        False,
        GLOBAL_INLINE_SCRIPTS,
        clientside_function,
        *args,
        **kwargs,
    )


def insert_callback(
    callback_list,
    callback_map,
    config_prevent_initial_callbacks,
    output,
    outputs_indices,
    inputs,
    state,
    inputs_state_indices,
    prevent_initial_call,
):
    if prevent_initial_call is None:
        prevent_initial_call = config_prevent_initial_callbacks

    callback_id = create_callback_id(output)
    callback_spec = {
        "output": callback_id,
        "inputs": [c.to_dict() for c in inputs],
        "state": [c.to_dict() for c in state],
        "clientside_function": None,
        "prevent_initial_call": prevent_initial_call,
    }
    callback_map[callback_id] = {
        "inputs": callback_spec["inputs"],
        "state": callback_spec["state"],
        "outputs_indices": outputs_indices,
        "inputs_state_indices": inputs_state_indices,
    }
    callback_list.append(callback_spec)

    return callback_id


def register_callback(
    callback_list, callback_map, config_prevent_initial_callbacks, *_args, **_kwargs
):
    (
        output,
        flat_inputs,
        flat_state,
        inputs_state_indices,
        prevent_initial_call,
    ) = handle_grouped_callback_args(_args, _kwargs)
    if isinstance(output, Output):
        # Insert callback with scalar (non-multi) Output
        insert_output = output
        multi = False
    else:
        # Insert callback as multi Output
        insert_output = flatten_grouping(output)
        multi = True

    output_indices = make_grouping_by_index(output, list(range(grouping_len(output))))
    callback_id = insert_callback(
        callback_list,
        callback_map,
        config_prevent_initial_callbacks,
        insert_output,
        output_indices,
        flat_inputs,
        flat_state,
        inputs_state_indices,
        prevent_initial_call,
    )

    # pylint: disable=too-many-locals
    def wrap_func(func):
        @wraps(func)
        def add_context(*args, **kwargs):
            output_spec = kwargs.pop("outputs_list")
            _validate.validate_output_spec(insert_output, output_spec, Output)

            func_args, func_kwargs = _validate.validate_and_group_input_args(
                args, inputs_state_indices
            )

            # don't touch the comment on the next line - used by debugger
            output_value = func(*func_args, **func_kwargs)  # %% callback invoked %%

            if isinstance(output_value, NoUpdate):
                raise PreventUpdate

            if not multi:
                output_value, output_spec = [output_value], [output_spec]
                flat_output_values = output_value
            else:
                if isinstance(output_value, (list, tuple)):
                    # For multi-output, allow top-level collection to be
                    # list or tuple
                    output_value = list(output_value)

                # Flatten grouping and validate grouping structure
                flat_output_values = flatten_grouping(output_value, output)

            _validate.validate_multi_return(
                output_spec, flat_output_values, callback_id
            )

            component_ids = collections.defaultdict(dict)
            has_update = False
            for val, spec in zip(flat_output_values, output_spec):
                if isinstance(val, NoUpdate):
                    continue
                for vali, speci in (
                    zip(val, spec) if isinstance(spec, list) else [[val, spec]]
                ):
                    if not isinstance(vali, NoUpdate):
                        has_update = True
                        id_str = stringify_id(speci["id"])
                        component_ids[id_str][speci["property"]] = vali

            if not has_update:
                raise PreventUpdate

            response = {"response": component_ids, "multi": True}

            try:
                jsonResponse = to_json(response)
            except TypeError:
                _validate.fail_callback_output(output_value, output)

            return jsonResponse

        callback_map[callback_id]["callback"] = add_context

        return func

    return wrap_func


_inline_clientside_template = """
var clientside = window.dash_clientside = window.dash_clientside || {{}};
var ns = clientside["{namespace}"] = clientside["{namespace}"] || {{}};
ns["{function_name}"] = {clientside_function};
"""


def register_clientside_callback(
    callback_list,
    callback_map,
    config_prevent_initial_callbacks,
    inline_scripts,
    clientside_function,
    *args,
    **kwargs,
):
    output, inputs, state, prevent_initial_call = handle_callback_args(args, kwargs)
    insert_callback(
        callback_list,
        callback_map,
        config_prevent_initial_callbacks,
        output,
        None,
        inputs,
        state,
        None,
        prevent_initial_call,
    )

    # If JS source is explicitly given, create a namespace and function
    # name, then inject the code.
    if isinstance(clientside_function, str):

        out0 = output
        if isinstance(output, (list, tuple)):
            out0 = output[0]

        namespace = f"_dashprivate_{out0.component_id}"
        function_name = out0.component_property

        inline_scripts.append(
            _inline_clientside_template.format(
                namespace=namespace.replace('"', '\\"'),
                function_name=function_name.replace('"', '\\"'),
                clientside_function=clientside_function,
            )
        )

    # Callback is stored in an external asset.
    else:
        namespace = clientside_function.namespace
        function_name = clientside_function.function_name

    callback_list[-1]["clientside_function"] = {
        "namespace": namespace,
        "function_name": function_name,
    }
