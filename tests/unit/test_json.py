import datetime
import decimal
import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import pytest
from plotly.io.json import to_json_plotly

from dash import dcc, html
from dash._utils import to_json


@pytest.fixture(params=["orjson", "json"])
def engine(request):
    original = pio.json.config.default_engine
    pio.json.config.default_engine = request.param
    yield request.param
    pio.json.config.default_engine = original


VALUES = {
    "component": html.Div([html.P("a"), dcc.Graph(figure=go.Figure(go.Bar(y=[1, 2])))]),
    "figure": go.Figure(go.Scatter(x=[1, 2], y=np.array([1.5, 2.5]))),
    "trace": go.Scatter(y=np.arange(3)),
    "timestamp": pd.Timestamp("2024-01-01 12:00"),
    "timestamp_utc": pd.Timestamp("2024-01-01", tz="UTC"),
    "timestamp_ns": pd.Timestamp("2024-01-01 00:00:00.123456789"),
    "nat": pd.NaT,
    "na": pd.NA,
    "datetime_index": pd.date_range("2024", periods=3),
    "series": pd.Series([1.5, np.nan]),
    "numpy_float": np.float64(1.5),
    "numpy_int": np.int64(3),
    "noncontiguous": np.arange(10.0)[::2],
    "object_array": np.array([1, "a", None], dtype=object),
    "masked": np.ma.masked,
    "decimal": decimal.Decimal("1.5"),
    "date": datetime.date(2024, 1, 1),
    "datetimes": [datetime.datetime(2024, 1, 1, 5)],
    "nan": [float("nan"), float("inf")],
    "int_keys": {1: "a"},
    "unsafe": "</script> ",
}


@pytest.mark.parametrize("name", list(VALUES))
def test_json001_matches_plotly(engine, name):
    payload = {"multi": True, "response": {"a": {"v": VALUES[name]}}}
    assert to_json(payload) == to_json_plotly(payload)
    with_div = {"v": VALUES[name], "d": html.Div("ok")}
    assert json.loads(to_json(with_div)) == json.loads(to_json_plotly(with_div))


def test_json002_converts_only_the_values_it_cannot_take(engine, monkeypatch):
    visited = []
    walk = pio._json.clean_to_json_compatible

    def counting(obj, **kwargs):
        visited.append(obj)
        return walk(obj, **kwargs)

    monkeypatch.setattr("plotly.io._json.clean_to_json_compatible", counting)
    monkeypatch.setattr("dash._json.clean_to_json_compatible", counting)
    points = [float(i) for i in range(10_000)]
    figure = go.Figure(go.Scatter(y=points)).to_plotly_json()
    response = {
        "multi": True,
        "response": {
            "graph": {"figure": figure},
            "status": {"children": html.Div("ok")},
            "store": {"data": pd.Timestamp("2024-01-01")},
        },
    }
    out = json.loads(to_json(response))
    assert out["response"]["graph"]["figure"]["data"][0]["y"] == points
    assert out["response"]["store"]["data"] == "2024-01-01T00:00:00"
    assert len(visited) < 10


def test_json003_datetime_series_with_nat(engine):
    # plotly's orjson path raises on this one
    series = pd.Series([pd.Timestamp("2024-01-01"), pd.NaT])
    assert json.loads(to_json({"v": series})) == {"v": ["2024-01-01T00:00:00", None]}


@pytest.mark.parametrize("value", [object(), 1j, {(1, 2): 1}, {"a": [{(1,): 2}]}])
def test_json004_unserializable_raises_type_error(engine, value):
    with pytest.raises(TypeError):
        to_json({"v": value})
