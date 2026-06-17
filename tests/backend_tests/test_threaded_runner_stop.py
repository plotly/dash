import threading
import time

import pytest

from dash import Dash, Input, Output, dcc, html
from dash.testing.application_runners import ThreadedRunner


def test_quart_threaded_runner_stop_is_graceful_and_bounded():
    """Regression test: ``ThreadedRunner.stop()`` must not hang for a Quart app.

    ``stop()`` only had a graceful-shutdown branch for FastAPI (keyed on
    ``_uvicorn_server``). A Quart app fell through to ``thread.kill()`` followed
    by an unbounded ``thread.join()``. The server thread is parked in a blocking
    syscall (IOCP on Windows, epoll on POSIX), so the injected ``SystemExit`` is
    not delivered promptly and ``join()`` can block forever.

    ``stop()`` now signals the Quart backend's cooperative shutdown event
    (``backend._ws_shutdown_event``) on the server's own loop and joins bounded
    by ``stop_timeout``.
    """
    pytest.importorskip("quart", reason="Quart extra dependencies are not installed")
    pytest.importorskip("hypercorn", reason="hypercorn is not installed")

    app = Dash(__name__, backend="quart")
    app.layout = html.Div(
        [dcc.Input(id="input", value="initial value"), html.Div(id="output")]
    )

    @app.callback(Output("output", "children"), Input("input", "value"))
    def update_output(value):
        return value

    runner = ThreadedRunner(stop_timeout=3)
    runner.host = "127.0.0.1"
    runner.start(app, host="127.0.0.1")

    try:
        # Sanity: a Quart app does NOT take the FastAPI graceful branch ...
        assert not hasattr(app, "_uvicorn_server")
        # ... but its backend does expose the cooperative shutdown switch.
        assert getattr(app.backend, "_ws_shutdown_event", None) is not None

        # Run stop() under a watchdog so a regression fails fast instead of
        # wedging the whole suite. The graceful path never calls thread.kill(),
        # so this watchdog thread is safe; a regression to the kill path would
        # inject SystemExit here and leave `done` unset -> the assertion below
        # fails (bounded) rather than hanging forever.
        done = threading.Event()

        def _stop():
            runner.stop()
            done.set()

        start = time.monotonic()
        threading.Thread(target=_stop, daemon=True).start()
        returned = done.wait(timeout=runner.stop_timeout + 5)
        elapsed = time.monotonic() - start

        assert returned, (
            "ThreadedRunner.stop() did not return for a Quart app within "
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
