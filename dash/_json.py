"""JSON for callback responses, layouts and the other payloads Dash sends.

plotly's ``to_json_plotly`` hands the whole payload to orjson, and when one
value is not orjson-native (a component, a figure, a ``pd.Timestamp``) it
walks every value in Python and dumps again. Here the encoder converts only
the values it cannot take itself: orjson when installed, otherwise msgspec,
which Dash already depends on. Anything either fails on goes to plotly, so the
output and the errors stay plotly's.
"""
import msgspec

# pylint: disable-next=import-error
from _plotly_utils.optional_imports import get_module  # type: ignore[import-untyped]
from plotly.io._json import (  # type: ignore[import-untyped]
    _safe,
    _swap_orjson,
    clean_to_json_compatible,
    config,
    to_json_plotly,
)


def _modules():
    return {
        "sage_all": get_module("sage.all", should_load=False),
        "np": get_module("numpy", should_load=False),
        "pd": get_module("pandas", should_load=False),
        "image": get_module("PIL.Image", should_load=False),
    }


def _convert(value, native):
    if isinstance(value, (dict, list, tuple)):
        # the encoder only asks about these when they sit where JSON can't
        # hold them (a tuple dict key); converting would loop forever
        raise TypeError(f"Type is not JSON serializable: {type(value).__name__}")
    to_plotly_json = getattr(value, "to_plotly_json", None)
    if to_plotly_json is not None:
        return to_plotly_json()
    cleaned = clean_to_json_compatible(
        value, numpy_allowed=native, datetime_allowed=native, modules=_modules()
    )
    if cleaned is value:
        raise TypeError(f"Type is not JSON serializable: {type(value).__name__}")
    return cleaned


def _orjson_default(value):
    return _convert(value, native=True)


def _msgspec_hook(value):
    # numpy scalars subclass float and int, but msgspec takes only exact types
    if isinstance(value, float):
        return float(value)
    if isinstance(value, int):
        return int(value)
    pd = get_module("pandas", should_load=False)
    if pd is not None:
        if value is pd.NaT:
            return None
        # isoformat keeps nanoseconds, which to_pydatetime drops
        if isinstance(value, pd.Timestamp):
            return value.isoformat()
        if isinstance(value, (pd.Series, pd.Index)) and value.dtype.kind == "M":
            return value.tolist()
    return _convert(value, native=False)


_msgspec_encoder = msgspec.json.Encoder(enc_hook=_msgspec_hook, decimal_format="number")


def to_json(value):
    orjson = (
        get_module("orjson", should_load=True)
        if config.default_engine != "json"
        else None
    )
    try:
        if orjson is not None:
            out = orjson.dumps(
                value,
                default=_orjson_default,
                option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY,
            )
        else:
            out = _msgspec_encoder.encode(value)
    except (TypeError, ValueError, OverflowError):
        return to_json_plotly(value)
    return _safe(out.decode("utf8"), _swap_orjson)
