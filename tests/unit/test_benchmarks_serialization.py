import json

from benchmarks.serialization import bench


def test_each_engine_runs_every_case_and_json_never_loads_orjson(tmp_path):
    out = tmp_path / "results.json"
    cases = [
        "list_float+none",
        "list_float+div",
        "list_datetime+figure",
        "numpy+layout",
    ]
    bench.main(
        [
            "--traces",
            "1",
            "--points",
            "50",
            "--repeat",
            "1",
            "--out",
            str(out),
            "--case",
            *cases,
        ]
    )
    run = json.loads(out.read_text())
    assert run["meta"]["orjson_loaded"] == {"orjson": True, "json": False}
    assert list(run["results"]) == cases
    for by_engine in run["results"].values():
        assert set(by_engine) == {"orjson", "json"}
        assert by_engine["orjson"]["median"] > 0
    assert run["meta"]["labels"]["list_float+div"] == "list of float, + html.Div"
