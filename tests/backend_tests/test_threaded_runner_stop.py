import threading
import time

import pytest

from dash import Dash, Input, Output, dcc, html
from dash.testing.application_runners import ThreadedRunner


@pytest.mark.parametrize("backend", ["flask", "quart", "fastapi"])
def test_threaded_runner_stop_is_bounded(backend):
    """Regression test: ``ThreadedRunner.stop()`` must return within the timeout
    for every backend instead of wedging the suite -- both the graceful ASGI
    path (quart/fastapi) and Flask's ``thread.kill()`` path.
    """

    if backend == "quart":
        pytest.importorskip(
            "quart", reason="Quart extra dependencies are not installed"
        )
        pytest.importorskip("hypercorn", reason="hypercorn is not installed")
    elif backend == "fastapi":
        pytest.importorskip(
            "fastapi", reason="fastapi extra dependencies are not installed"
        )

    app = Dash(__name__, backend=backend)
    app.layout = html.Div(
        [dcc.Input(id="input", value="initial value"), html.Div(id="output")]
    )

    @app.callback(Output("output", "children"), Input("input", "value"))
    def update_output(value):
        return value

    runner = ThreadedRunner(stop_timeout=3)
    runner.host = "127.0.0.1"

    # Run stop() in a watchdog so a regression fails the assertion instead of
    # hanging the suite. The watchdog is started BEFORE runner.start(): Flask's
    # stop() -> thread.kill() injects SystemExit into every thread created after
    # the KillerThread, so a watchdog spawned afterwards would kill itself.
    # Starting it first lands it in KillerThread._old_threads, which kill() skips
    # -- harmless for the graceful backends, which never call kill().
    done = threading.Event()
    go = threading.Event()

    def _stop():
        go.wait()
        runner.stop()
        done.set()

    threading.Thread(target=_stop, daemon=True).start()
    runner.start(app, host="127.0.0.1")

    try:
        start = time.monotonic()
        go.set()
        returned = done.wait(timeout=runner.stop_timeout + 5)
        elapsed = time.monotonic() - start

        assert returned, (
            f"ThreadedRunner.stop() did not return for a {backend} app within "
            f"{runner.stop_timeout + 5}s -- regression of the teardown hang"
        )
        assert elapsed < runner.stop_timeout + 2
        assert not runner.thread.is_alive()
        assert runner.started is False
    finally:
        if runner.started:
            try:
                runner.stop()
            except Exception:  # pylint: disable=broad-except
                pass
