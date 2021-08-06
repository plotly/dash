from dash.dependencies import Input
from dash._grouping import (
    flatten_grouping,
    make_grouping_by_index,
    grouping_len,
    map_grouping,
    make_grouping_by_key,
    validate_grouping,
    SchemaTypeValidationError,
    SchemaLengthValidationError,
    SchemaKeysValidationError,
)
from fixtures import (  # noqa: F401
    scalar_grouping_size,
    list_grouping_size,
    dict_grouping_size,
    mixed_grouping_size,
)
import string
import pytest


# Test flatten_grouping and grouping_len
def test_flatten_scalar(scalar_grouping_size):
    grouping, size = scalar_grouping_size
    expected = list(range(size))
    result = flatten_grouping(grouping)
    assert expected == result
    assert len(result) == grouping_len(grouping)


def test_flatten_list(list_grouping_size):
    grouping, size = list_grouping_size
    expected = list(range(size))
    result = flatten_grouping(grouping)
    assert expected == result
    assert len(result) == grouping_len(grouping)


def test_flatten_dict(dict_grouping_size):
    grouping, size = dict_grouping_size
    expected = list(range(size))
    result = flatten_grouping(grouping)
    assert expected == result
    assert len(result) == grouping_len(grouping)


def test_flatten_dict_key_order(dict_grouping_size):
    grouping, size = dict_grouping_size
    expected = list(range(size))

    # Reverse key order of value dict to make sure order is preserved
    rev_grouping = {k: grouping[k] for k in reversed(list(grouping.keys()))}
    result = flatten_grouping(rev_grouping, grouping)
    assert expected == result
    assert len(result) == grouping_len(grouping)


def test_flatten_mixed(mixed_grouping_size):
    grouping, size = mixed_grouping_size
    expected = list(range(size))
    result = flatten_grouping(grouping)
    assert expected == result
    assert len(result) == grouping_len(grouping)


def test_flatten_odd_value():
    # Anything other than tuple and dict should be treated as a
    # scalar and passed through
    expected = [0, sum, Input("foo", "bar")]
    vals_collection = (0, (sum, Input("foo", "bar")))
    result = flatten_grouping(vals_collection)
    assert expected == result
    assert len(result) == grouping_len(vals_collection)


# Test make_grouping_by_position
def make_flat_values(size):
    return list(string.ascii_lowercase[:size])


def test_make_grouping_by_position_scalar(scalar_grouping_size):
    grouping, size = scalar_grouping_size
    flat_values = make_flat_values(size)
    result = make_grouping_by_index(grouping, flat_values)
    expected = flat_values[0]
    assert expected == result


def test_make_grouping_by_position_list(list_grouping_size):
    grouping, size = list_grouping_size
    flat_values = make_flat_values(size)
    result = make_grouping_by_index(grouping, flat_values)
    expected = flat_values
    assert expected == result


def test_make_grouping_by_position_dict(dict_grouping_size):
    grouping, size = dict_grouping_size
    flat_values = make_flat_values(size)
    result = make_grouping_by_index(grouping, flat_values)
    expected = {k: flat_values[i] for i, k in enumerate(grouping)}
    assert expected == result


def test_make_grouping_by_position_mixed(mixed_grouping_size):
    grouping, size = mixed_grouping_size
    flat_values = make_flat_values(size)
    result = make_grouping_by_index(grouping, flat_values)

    # Check for size mutation on flat_values
    assert len(flat_values) == size

    # Check with stack-based algorithm as independent implementation
    groupings = [grouping]
    results = [result]
    while groupings:
        next_grouping = groupings.pop(0)
        next_result = results.pop(0)
        if isinstance(next_grouping, (tuple, list)):
            assert isinstance(next_result, (tuple, list))
            assert len(next_grouping) == len(next_result)
            groupings.extend(next_grouping)
            results.extend(next_result)
        elif isinstance(next_grouping, dict):
            assert isinstance(next_result, dict)
            assert list(next_result) == list(next_grouping)
            groupings.extend(next_grouping.values())
            results.extend(next_result.values())
        else:
            assert isinstance(next_grouping, int)
            assert flat_values[next_grouping] == next_result


# Test map_grouping
def test_map_grouping_scalar(scalar_grouping_size):
    grouping, size = scalar_grouping_size
    result = map_grouping(lambda x: x * 2 + 5, grouping)
    expected = grouping * 2 + 5
    assert expected == result


def test_map_grouping_list(list_grouping_size):
    grouping, size = list_grouping_size
    result = map_grouping(lambda x: x * 2 + 5, grouping)
    expected = [g * 2 + 5 for g in grouping]
    assert expected == result


def test_map_grouping_dict(dict_grouping_size):
    grouping, size = dict_grouping_size
    result = map_grouping(lambda x: x * 2 + 5, grouping)
    expected = {k: v * 2 + 5 for k, v in grouping.items()}
    assert expected == result


def test_map_grouping_mixed(mixed_grouping_size):
    grouping, size = mixed_grouping_size

    def fn(x):
        return x * 2 + 5

    result = map_grouping(fn, grouping)
    expected = make_grouping_by_index(
        grouping, list(map(fn, flatten_grouping(grouping)))
    )
    assert expected == result


# Test make_grouping_by_key
def make_key_source(size):
    return {i: string.ascii_lowercase[i] for i in range(size)}


def test_make_grouping_by_key_scalar(scalar_grouping_size):
    grouping, size = scalar_grouping_size
    source = make_key_source(size)
    result = make_grouping_by_key(grouping, source)
    expected = source[0]
    assert expected == result


def test_make_grouping_by_key_list(list_grouping_size):
    grouping, size = list_grouping_size
    source = make_key_source(size)
    result = make_grouping_by_key(grouping, source)
    expected = [source[i] for i in range(size)]
    assert expected == result


def test_make_grouping_by_key_dict(dict_grouping_size):
    grouping, size = dict_grouping_size
    source = make_key_source(size)
    result = make_grouping_by_key(grouping, source)
    expected = {k: source[v] for k, v in grouping.items()}
    assert expected == result


def test_make_grouping_by_key_mixed(mixed_grouping_size):
    grouping, size = mixed_grouping_size
    source = {i: string.ascii_lowercase[i] for i in range(size)}
    result = make_grouping_by_key(grouping, source)

    # Check with stack-based algorithm as independent implementation
    groupings = [grouping]
    results = [result]
    while groupings:
        next_grouping = groupings.pop(0)
        next_result = results.pop(0)
        if isinstance(next_grouping, (list, tuple)):
            assert isinstance(next_result, (list, tuple))
            assert len(next_grouping) == len(next_result)
            groupings.extend(next_grouping)
            results.extend(next_result)
        elif isinstance(next_grouping, dict):
            assert isinstance(next_result, dict)
            assert list(next_result) == list(next_grouping)
            groupings.extend(next_grouping.values())
            results.extend(next_result.values())
        else:
            assert source[next_grouping] == next_result


def test_make_grouping_by_key_default():
    grouping = (0, {"A": 1, "B": 2})
    source = make_key_source(2)
    result = make_grouping_by_key(grouping, source)
    expected = ["a", {"A": "b", "B": None}]
    assert expected == result

    # Custom default
    result = make_grouping_by_key(grouping, source, default="_missing_")
    expected = ["a", {"A": "b", "B": "_missing_"}]
    assert expected == result


# Test validate_schema
def make_schema_with_nones(grouping):
    """
    Create a grouping by replacing all grouping scalars values with None
    """
    return map_grouping(lambda _: None, grouping)


def test_validate_schema_grouping_scalar(scalar_grouping_size):
    grouping, size = scalar_grouping_size
    schema = make_schema_with_nones(grouping)
    validate_grouping(grouping, schema)

    # Anything is valid as a scalar
    validate_grouping((0,), schema)
    validate_grouping({"a": 0}, schema)


def test_validate_schema_grouping_list(list_grouping_size):
    grouping, size = list_grouping_size
    schema = make_schema_with_nones(grouping)
    validate_grouping(grouping, schema)

    # check validation failures
    with pytest.raises(SchemaTypeValidationError):
        validate_grouping(None, schema)

    with pytest.raises(SchemaLengthValidationError):
        validate_grouping((None,) * (size + 1), schema)

    with pytest.raises(SchemaTypeValidationError):
        validate_grouping({"a": 0}, schema)


def test_validate_schema_dict(dict_grouping_size):
    grouping, size = dict_grouping_size
    schema = make_schema_with_nones(grouping)
    validate_grouping(grouping, schema)

    # check validation failures
    with pytest.raises(SchemaTypeValidationError):
        validate_grouping(None, schema)

    with pytest.raises(SchemaTypeValidationError):
        validate_grouping((None,), schema)

    with pytest.raises(SchemaKeysValidationError):
        validate_grouping({"A": 0, "bogus": 2}, schema)


def test_validate_schema_mixed(mixed_grouping_size):
    grouping, size = mixed_grouping_size
    schema = make_schema_with_nones(grouping)
    validate_grouping(grouping, schema)

    # check validation failures
    with pytest.raises(SchemaTypeValidationError):
        validate_grouping(None, schema)

    # Check invalid list/tuple value
    if isinstance(schema, (list, tuple)):
        err = SchemaLengthValidationError
    else:
        err = SchemaTypeValidationError
    with pytest.raises(err):
        validate_grouping((None,), schema)

    # Check invalid dict value
    if isinstance(schema, dict):
        err = SchemaKeysValidationError
    else:
        err = SchemaTypeValidationError

    with pytest.raises(err):
        validate_grouping({"A": 0, "bogus": 2}, schema)
