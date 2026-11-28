import json
import subprocess
import sys
from types import SimpleNamespace

import psutil
import pytest

from benchmarks import loadkit

SETUP = loadkit.Setup("flask-gunicorn-w1", "flask", "gunicorn", 1, "Flask")


def _ok(browsers):
    return {
        "browsers": browsers,
        "saturated": False,
        "client_bound": False,
        "client_cpu_peak_pct": 0,
        "server_cpu_cores": 0,
        "error_rate": 0,
    }


def test_a_broken_point_is_recorded_not_dropped(tmp_path):
    args = SimpleNamespace(browsers=[100, 500, 1000], out=str(tmp_path / "r.json"))

    def run_point(_setup, browsers, _args):
        if browsers == 500:
            raise RuntimeError("clients still running 90s after the window")
        return _ok(browsers)

    complete = loadkit.sweep(
        {"setups": []}, [SETUP], args, run_point, lambda _p: "", lambda _s: {}
    )

    assert not complete

    (entry,) = json.loads((tmp_path / "r.json").read_text())["setups"]
    assert [p["browsers"] for p in entry["points"]] == [100]
    assert entry["failed"]["browsers"] == 500


@pytest.fixture
def allowed_4_to_7(monkeypatch):
    monkeypatch.setattr(loadkit.resource, "setrlimit", lambda *_: None)
    monkeypatch.setattr(
        psutil.Process, "cpu_affinity", lambda _self: [4, 5, 6, 7], raising=False
    )


@pytest.mark.usefixtures("allowed_4_to_7")
def test_cpus_are_split_within_the_allowed_set():
    args = SimpleNamespace(server_cpus=None)
    loadkit.configure(args)
    assert args.server_cpus == [4, 5]
    assert args.client_cpus == [6, 7]


@pytest.mark.usefixtures("allowed_4_to_7")
def test_server_cpus_must_be_allowed():
    with pytest.raises(SystemExit, match="within"):
        loadkit.configure(SimpleNamespace(server_cpus="0,4"))


def test_a_failed_pin_does_not_leak_the_server(tmp_path, monkeypatch):
    started = []
    popen = subprocess.Popen

    def recording_popen(*a, **kw):
        started.append(popen(*a, **kw))  # pylint: disable=consider-using-with
        return started[-1]

    def refuse(_self, _cpus=None):
        raise ValueError("invalid CPU")

    monkeypatch.setattr(loadkit.subprocess, "Popen", recording_popen)
    monkeypatch.setattr(
        loadkit,
        "server_cmd",
        lambda *_: [sys.executable, "-c", "import time; time.sleep(60)"],
    )
    monkeypatch.setattr(psutil.Process, "cpu_affinity", refuse, raising=False)

    with pytest.raises(ValueError):
        with loadkit.serve(SETUP, str(tmp_path), "app", {}, [99]):
            pass

    assert started[0].poll() is not None
