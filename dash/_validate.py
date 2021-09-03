import collections
import re
from textwrap import dedent

from ._grouping import grouping_len, map_grouping
from .development.base_component import Component
from . import exceptions
from ._utils import patch_collections_abc, stringify_id


def validate_callback(outputs, inputs, state, extra_args, types):
    Input, Output, State = types
    if extra_args:
        if not isinstance(extra_args[0], (Output, Input, State)):
            raise exceptions.IncorrectTypeException(
                dedent(
                    """
                    Callback arguments must be `Output`, `Input`, or `State` objects,
                    optionally wrapped in a list or tuple. We found (possibly after
                    unwrapping a list or tuple):
                    {}
                    """
                ).format(repr(extra_args[0]))
            )

        raise exceptions.IncorrectTypeException(
            dedent(
                """
                In a callback definition, you must provide all Outputs first,
                then all Inputs, then all States. After this item:
                {}
                we found this item next:
                {}
                """
            ).format(repr((outputs + inputs + state)[-1]), repr(extra_args[0]))
        )

    for args in [outputs, inputs, state]:
        for arg in args:
            validate_callback_arg(arg)


def validate_callback_arg(arg):
    if not isinstance(getattr(arg, "component_property", None), str):
        raise exceptions.IncorrectTypeException(
            dedent(
                """
                component_property must be a string, found {!r}
                """
            ).format(arg.component_property)
        )

    if hasattr(arg, "component_event"):
        raise exceptions.NonExistentEventException(
            """
            Events have been removed.
            Use the associated property instead.
            """
        )

    if isinstance(arg.component_id, dict):
        validate_id_dict(arg)

    elif isinstance(arg.component_id, str):
        validate_id_string(arg)

    else:
        raise exceptions.IncorrectTypeException(
            dedent(
                """
                component_id must be a string or dict, found {!r}
                """
            ).format(arg.component_id)
        )


def validate_id_dict(arg):
    arg_id = arg.component_id

    for k in arg_id:
        # Need to keep key type validation on the Python side, since
        # non-string keys will be converted to strings in json.dumps and may
        # cause unwanted collisions
        if not isinstance(k, str):
            raise exceptions.IncorrectTypeException(
                dedent(
                    """
                    Wildcard ID keys must be non-empty strings,
                    found {!r} in id {!r}
                    """
                ).format(k, arg_id)
            )


def validate_id_string(arg):
    arg_id = arg.component_id

    invalid_chars = ".{"
    invalid_found = [x for x in invalid_chars if x in arg_id]
    if invalid_found:
        raise exceptions.InvalidComponentIdError(
            """
            The element `{}` contains `{}` in its ID.
            Characters `{}` are not allowed in IDs.
            """.format(
                arg_id, "`, `".join(invalid_found), "`, `".join(invalid_chars)
            )
        )


def validate_output_spec(output, output_spec, Output):
    """
    This validation is for security and internal debugging, not for users,
    so the messages are not intended to be clear.
    `output` comes from the callback definition, `output_spec` from the request.
    """
    if not isinstance(output, (list, tuple)):
        output, output_spec = [output], [output_spec]
    elif len(output) != len(output_spec):
        raise exceptions.CallbackException("Wrong length output_spec")

    for outi, speci in zip(output, output_spec):
        speci_list = speci if isinstance(speci, (list, tuple)) else [speci]
        for specij in speci_list:
            if not Output(specij["id"], specij["property"]) == outi:
                raise exceptions.CallbackException(
                    "Output does not match callback definition"
                )


def validate_and_group_input_args(flat_args, arg_index_grouping):
    if grouping_len(arg_index_grouping) != len(flat_args):
        raise exceptions.CallbackException("Inputs do not match callback definition")

    args_grouping = map_grouping(lambda ind: flat_args[ind], arg_index_grouping)
    if isinstance(arg_index_grouping, dict):
        func_args = []
        func_kwargs = args_grouping
    elif isinstance(arg_index_grouping, (tuple, list)):
        func_args = list(args_grouping)
        func_kwargs = {}
    else:
        # Scalar input
        func_args = [args_grouping]
        func_kwargs = {}

    return func_args, func_kwargs


def validate_multi_return(outputs_list, output_value, callback_id):
    if not isinstance(output_value, (list, tuple)):
        raise exceptions.InvalidCallbackReturnValue(
            dedent(
                """
                The callback {} is a multi-output.
                Expected the output type to be a list or tuple but got:
                {}.
                """
            ).format(callback_id, repr(output_value))
        )

    if len(output_value) != len(outputs_list):
        raise exceptions.InvalidCallbackReturnValue(
            """
            Invalid number of output values for {}.
            Expected {}, got {}
            """.format(
                callback_id, len(outputs_list), len(output_value)
            )
        )

    for i, outi in enumerate(outputs_list):
        if isinstance(outi, list):
            vi = output_value[i]
            if not isinstance(vi, (list, tuple)):
                raise exceptions.InvalidCallbackReturnValue(
                    dedent(
                        """
                        The callback {} output {} is a wildcard multi-output.
                        Expected the output type to be a list or tuple but got:
                        {}.
                        output spec: {}
                        """
                    ).format(callback_id, i, repr(vi), repr(outi))
                )

            if len(vi) != len(outi):
                raise exceptions.InvalidCallbackReturnValue(
                    dedent(
                        """
                        Invalid number of output values for {} item {}.
                        Expected {}, got {}
                        output spec: {}
                        output value: {}
                        """
                    ).format(callback_id, i, len(vi), len(outi), repr(outi), repr(vi))
                )


def fail_callback_output(output_value, output):
    valid = (str, dict, int, float, type(None), Component)

    def _raise_invalid(bad_val, outer_val, path, index=None, toplevel=False):
        bad_type = type(bad_val).__name__
        outer_id = (
            "(id={:s})".format(outer_val.id) if getattr(outer_val, "id", False) else ""
        )
        outer_type = type(outer_val).__name__
        if toplevel:
            location = dedent(
                """
                The value in question is either the only value returned,
                or is in the top level of the returned list,
                """
            )
        else:
            index_string = "[*]" if index is None else "[{:d}]".format(index)
            location = dedent(
                """
                The value in question is located at
                {} {} {}
                {},
                """
            ).format(index_string, outer_type, outer_id, path)

        raise exceptions.InvalidCallbackReturnValue(
            dedent(
                """
                The callback for `{output}`
                returned a {object:s} having type `{type}`
                which is not JSON serializable.

                {location}
                and has string representation
                `{bad_val}`

                In general, Dash properties can only be
                dash components, strings, dictionaries, numbers, None,
                or lists of those.
                """
            ).format(
                output=repr(output),
                object="tree with one value" if not toplevel else "value",
                type=bad_type,
                location=location,
                bad_val=bad_val,
            )
        )

    def _value_is_valid(val):
        return isinstance(val, valid)

    def _validate_value(val, index=None):
        # val is a Component
        if isinstance(val, Component):
            # pylint: disable=protected-access
            for p, j in val._traverse_with_paths():
                # check each component value in the tree
                if not _value_is_valid(j):
                    _raise_invalid(bad_val=j, outer_val=val, path=p, index=index)

                # Children that are not of type Component or
                # list/tuple not returned by traverse
                child = getattr(j, "children", None)
                if not isinstance(child, (tuple, collections.MutableSequence)):
                    if child and not _value_is_valid(child):
                        _raise_invalid(
                            bad_val=child,
                            outer_val=val,
                            path=p + "\n" + "[*] " + type(child).__name__,
                            index=index,
                        )

            # Also check the child of val, as it will not be returned
            child = getattr(val, "children", None)
            if not isinstance(child, (tuple, collections.MutableSequence)):
                if child and not _value_is_valid(child):
                    _raise_invalid(
                        bad_val=child,
                        outer_val=val,
                        path=type(child).__name__,
                        index=index,
                    )

        # val is not a Component, but is at the top level of tree
        elif not _value_is_valid(val):
            _raise_invalid(
                bad_val=val,
                outer_val=type(val).__name__,
                path="",
                index=index,
                toplevel=True,
            )

    if isinstance(output_value, list):
        for i, val in enumerate(output_value):
            _validate_value(val, index=i)
    else:
        _validate_value(output_value)

    # if we got this far, raise a generic JSON error
    raise exceptions.InvalidCallbackReturnValue(
        """
        The callback for property `{property:s}` of component `{id:s}`
        returned a value which is not JSON serializable.

        In general, Dash properties can only be dash components, strings,
        dictionaries, numbers, None, or lists of those.
        """.format(
            property=output.component_property, id=output.component_id
        )
    )


def check_obsolete(kwargs):
    for key in kwargs:
        if key in ["components_cache_max_age", "static_folder"]:
            raise exceptions.ObsoleteKwargException(
                """
                {} is no longer a valid keyword argument in Dash since v1.0.
                See https://dash.plotly.com for details.
                """.format(
                    key
                )
            )
        # any other kwarg mimic the built-in exception
        raise TypeError("Dash() got an unexpected keyword argument '" + key + "'")


def validate_js_path(registered_paths, package_name, path_in_package_dist):
    if package_name not in registered_paths:
        raise exceptions.DependencyException(
            """
            Error loading dependency. "{}" is not a registered library.
            Registered libraries are:
            {}
            """.format(
                package_name, list(registered_paths.keys())
            )
        )

    if path_in_package_dist not in registered_paths[package_name]:
        raise exceptions.DependencyException(
            """
            "{}" is registered but the path requested is not valid.
            The path requested: "{}"
            List of registered paths: {}
            """.format(
                package_name, path_in_package_dist, registered_paths
            )
        )


def validate_index(name, checks, index):
    missing = [i for check, i in checks if not re.compile(check).search(index)]
    if missing:
        plural = "s" if len(missing) > 1 else ""
        raise exceptions.InvalidIndexException(
            "Missing item{pl} {items} in {name}.".format(
                items=", ".join(missing), pl=plural, name=name
            )
        )


def validate_layout_type(value):
    if not isinstance(value, (Component, patch_collections_abc("Callable"))):
        raise exceptions.NoLayoutException(
            "Layout must be a dash component "
            "or a function that returns a dash component."
        )


def validate_layout(layout, layout_value):
    if layout is None:
        raise exceptions.NoLayoutException(
            """
            The layout was `None` at the time that `run_server` was called.
            Make sure to set the `layout` attribute of your application
            before running the server.
            """
        )

    layout_id = stringify_id(getattr(layout_value, "id", None))

    component_ids = {layout_id} if layout_id else set()
    for component in layout_value._traverse():  # pylint: disable=protected-access
        component_id = stringify_id(getattr(component, "id", None))
        if component_id and component_id in component_ids:
            raise exceptions.DuplicateIdError(
                """
                Duplicate component id found in the initial layout: `{}`
                """.format(
                    component_id
                )
            )
        component_ids.add(component_id)
