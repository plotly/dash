def _insert_callback(
    output,
    outputs_indices,
    inputs,
    state,
    inputs_state_indices,
    prevent_initial_call,
):
    if prevent_initial_call is None:
        prevent_initial_call = self.config.prevent_initial_callbacks

    callback_id = create_callback_id(output)
    callback_spec = {
        "output": callback_id,
        "inputs": [c.to_dict() for c in inputs],
        "state": [c.to_dict() for c in state],
        "clientside_function": None,
        "prevent_initial_call": prevent_initial_call,
    }
    self.callback_map[callback_id] = {
        "inputs": callback_spec["inputs"],
        "state": callback_spec["state"],
        "outputs_indices": outputs_indices,
        "inputs_state_indices": inputs_state_indices,
    }
    self._callback_list.append(callback_spec)

    return callback_id


def _callback(*_args, **_kwargs):
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

    output_indices = make_grouping_by_index(
        output, list(range(grouping_len(output)))
    )
    callback_id = self._insert_callback(
        insert_output,
        output_indices,
        flat_inputs,
        flat_state,
        inputs_state_indices,
        prevent_initial_call,
    )

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

            if isinstance(output_value, _NoUpdate):
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

        self.callback_map[callback_id]["callback"] = add_context

        return add_context

    return wrap_func
