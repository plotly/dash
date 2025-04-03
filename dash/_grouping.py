"""
This module contains a collection of utility function for dealing with property
groupings.

Terminology:

For the purpose of grouping and ungrouping, tuples/lists and dictionaries are considered
"composite values" and all other values are considered "scalar values".

A "grouping value" is either composite or scalar.

A "schema" is a grouping value that can be used to encode an expected grouping
structure

"""
from .exceptions import InvalidCallbackReturnValue
from ._utils import AttributeDict, stringify_id


def flatten_grouping(grouping, schema=None):
    """
    Convert a grouping value to a list of scalar values

    :param grouping: grouping value to flatten
    :param schema: If provided, a grouping value representing the expected structure of
        the input grouping value. If not provided, the grouping value is its own schema.
        A schema is required in order to be able treat tuples and dicts in the input
        grouping as scalar values.

    :return: list of the scalar values in the input grouping
    """
    if schema is None:
        schema = grouping
    else:
        validate_grouping(grouping, schema)

    if isinstance(schema, (tuple, list)):
        return [
            g
            for group_el, schema_el in zip(grouping, schema)
            for g in flatten_grouping(group_el, schema_el)
        ]

    if isinstance(schema, dict):
        return [g for k in schema for g in flatten_grouping(grouping[k], schema[k])]

    return [grouping]


def grouping_len(grouping):
    """
    Get the length of a grouping. The length equal to the number of scalar values
    contained in the grouping, which is equivalent to the length of the list that would
    result from calling flatten_grouping on the grouping value.

    :param grouping: The grouping value to calculate the length of
    :return: non-negative integer
    """
    if isinstance(grouping, (tuple, list)):
        return sum([grouping_len(group_el) for group_el in grouping])

    if isinstance(grouping, dict):
        return sum([grouping_len(group_el) for group_el in grouping.values()])

    return 1


def make_grouping_by_index(schema, flat_values):
    """
    Make a grouping like the provided grouping schema, with scalar values drawn from a
    flat list by index.

    Note: Scalar values in schema are not used

    :param schema: Grouping value encoding the structure of the grouping to return
    :param flat_values: List of values with length matching the grouping_len of schema.
        Elements of flat_values will become the scalar values in the resulting grouping
    """

    def _perform_make_grouping_like(value, next_values):
        if isinstance(value, (tuple, list)):
            return list(
                _perform_make_grouping_like(el, next_values)
                for i, el in enumerate(value)
            )

        if isinstance(value, dict):
            return {
                k: _perform_make_grouping_like(v, next_values)
                for i, (k, v) in enumerate(value.items())
            }

        return next_values.pop(0)

    if not isinstance(flat_values, list):
        raise ValueError(
            "The flat_values argument must be a list. "
            f"Received value of type {type(flat_values)}"
        )

    expected_length = len(flatten_grouping(schema))
    if len(flat_values) != expected_length:
        raise ValueError(
            f"The specified grouping pattern requires {expected_length} "
            f"elements but received {len(flat_values)}\n"
            f"    Grouping pattern: {repr(schema)}\n"
            f"    Values: {flat_values}"
        )

    return _perform_make_grouping_like(schema, list(flat_values))


def map_grouping(fn, grouping):
    """
    Map a function over all of the scalar values of a grouping, maintaining the
    grouping structure

    :param fn: Single-argument function that accepts and returns scalar grouping values
    :param grouping: The grouping to map the function over
    :return: A new grouping with the same structure as input grouping with scalar
        values updated by the input function.
    """
    if isinstance(grouping, (tuple, list)):
        return [map_grouping(fn, g) for g in grouping]

    if isinstance(grouping, dict):
        return AttributeDict({k: map_grouping(fn, g) for k, g in grouping.items()})

    return fn(grouping)


def make_grouping_by_key(schema, source, default=None):
    """
    Create a grouping from a schema by using the schema's scalar values to look up
    items in the provided source object.

    :param schema: A grouping of potential keys in source
    :param source: Dict-like object to use to look up scalar grouping value using
        scalar grouping values as keys
    :param default: Default scalar value to use if grouping scalar key is not present
        in source
    :return: grouping
    """
    return map_grouping(lambda s: source.get(s, default), schema)


class SchemaTypeValidationError(InvalidCallbackReturnValue):
    def __init__(self, value, full_schema, path, expected_type):
        super().__init__(
            msg=f"""
                Schema: {full_schema}
                Path: {repr(path)}
                Expected type: {expected_type}
                Received value of type {type(value)}:
                    {repr(value)}
                """
        )

    @classmethod
    def check(cls, value, full_schema, path, expected_type):
        if not isinstance(value, expected_type):
            raise SchemaTypeValidationError(value, full_schema, path, expected_type)


class SchemaLengthValidationError(InvalidCallbackReturnValue):
    def __init__(self, value, full_schema, path, expected_len):
        super().__init__(
            msg=f"""
                Schema: {full_schema}
                Path: {repr(path)}
                Expected length: {expected_len}
                Received value of length {len(value)}:
                    {repr(value)}
                """
        )

    @classmethod
    def check(cls, value, full_schema, path, expected_len):
        if len(value) != expected_len:
            raise SchemaLengthValidationError(value, full_schema, path, expected_len)


class SchemaKeysValidationError(InvalidCallbackReturnValue):
    def __init__(self, value, full_schema, path, expected_keys):
        super().__init__(
            msg=f"""
                Schema: {full_schema}
                Path: {repr(path)}
                Expected keys: {expected_keys}
                Received value with keys {set(value.keys())}:
                    {repr(value)}
                """
        )

    @classmethod
    def check(cls, value, full_schema, path, expected_keys):
        if set(value.keys()) != set(expected_keys):
            raise SchemaKeysValidationError(value, full_schema, path, expected_keys)


def validate_grouping(grouping, schema, full_schema=None, path=()):
    """
    Validate that the provided grouping conforms to the provided schema.
    If not, raise a SchemaValidationError
    """
    if full_schema is None:
        full_schema = schema

    if isinstance(schema, (tuple, list)):
        SchemaTypeValidationError.check(grouping, full_schema, path, (tuple, list))
        SchemaLengthValidationError.check(grouping, full_schema, path, len(schema))

        for i, (g, s) in enumerate(zip(grouping, schema)):
            validate_grouping(g, s, full_schema=full_schema, path=path + (i,))
    elif isinstance(schema, dict):
        SchemaTypeValidationError.check(grouping, full_schema, path, dict)
        SchemaKeysValidationError.check(grouping, full_schema, path, set(schema))

        for k in schema:
            validate_grouping(
                grouping[k], schema[k], full_schema=full_schema, path=path + (k,)
            )
    else:
        pass


def update_args_group(g, triggered):
    if isinstance(g, dict):
        str_id = stringify_id(g["id"])
        prop_id = f"{str_id}.{g['property']}"

        new_values = {
            "value": g.get("value"),
            "str_id": str_id,
            "triggered": prop_id in triggered,
            "id": AttributeDict(g["id"]) if isinstance(g["id"], dict) else g["id"],
        }
        g.update(new_values)
