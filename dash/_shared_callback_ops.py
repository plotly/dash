import collections
from functools import wraps
import json
import plotly

from .exceptions import PreventUpdate
from ._utils import (
    create_callback_id,
    stringify_id,
)
from .dependencies import handle_callback_args, Output
from . import _validate

class _NoUpdate(object):
    # pylint: disable=too-few-public-methods
    pass



def _insert_callback(callback_list, callback_map, config_prevent_initial_callbacks,
        output, inputs, state, prevent_initial_call):

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
    }
    callback_list.append(callback_spec)

    return callback_id


def _register_callback(
        callback_list, callback_map,
        config_prevent_initial_callbacks,
        *_args, **_kwargs):
    output, inputs, state, prevent_initial_call = handle_callback_args(
        _args, _kwargs
    )
    callback_id = _insert_callback(
        callback_list, callback_map, config_prevent_initial_callbacks,
        output, inputs, state, prevent_initial_call)
    multi = isinstance(output, (list, tuple))

    def wrap_func(func):
        @wraps(func)
        def add_context(*args, **kwargs):
            output_spec = kwargs.pop("outputs_list")
            _validate.validate_output_spec(output, output_spec, Output)

            # don't touch the comment on the next line - used by debugger
            output_value = func(*args, **kwargs)  # %% callback invoked %%

            if isinstance(output_value, _NoUpdate):
                raise PreventUpdate

            # wrap single outputs so we can treat them all the same
            # for validation and response creation
            if not multi:
                output_value, output_spec = [output_value], [output_spec]

            _validate.validate_multi_return(output_spec, output_value, callback_id)

            component_ids = collections.defaultdict(dict)
            has_update = False
            for val, spec in zip(output_value, output_spec):
                if isinstance(val, _NoUpdate):
                    continue
                for vali, speci in (
                    zip(val, spec) if isinstance(spec, list) else [[val, spec]]
                ):
                    if not isinstance(vali, _NoUpdate):
                        has_update = True
                        id_str = stringify_id(speci["id"])
                        component_ids[id_str][speci["property"]] = vali

            if not has_update:
                raise PreventUpdate

            response = {"response": component_ids, "multi": True}

            try:
                jsonResponse = json.dumps(
                    response, cls=plotly.utils.PlotlyJSONEncoder
                )
            except TypeError:
                _validate.fail_callback_output(output_value, output)

            return jsonResponse

        callback_map[callback_id]["callback"] = add_context

        return add_context

    return wrap_func
