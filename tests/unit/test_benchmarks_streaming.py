"""Multi-worker streaming setups run on local shared storage, never skipped."""
from types import SimpleNamespace

from benchmarks import loadkit
from benchmarks.streaming import load


def test_every_setup_runs_without_redis(tmp_path):
    args = SimpleNamespace(browsers=[10], out=str(tmp_path / "results.json"))
    results = {"setups": []}

    def run_point(_setup, browsers, _args):
        return {
            "browsers": browsers,
            "saturated": False,
            "client_bound": False,
            "client_cpu_peak_pct": 0,
            "server_cpu_cores": 0,
            "error_rate": 0,
        }

    loadkit.sweep(
        results, load.SETUPS, args, run_point, lambda _p: "", load._entry_fields
    )

    ran = {s["name"]: s for s in results["setups"]}
    assert set(ran) == {s.name for s in load.SETUPS}
    assert any(s.workers > 1 for s in load.SETUPS)
    assert all(s["storage"] == "local" for s in ran.values())
