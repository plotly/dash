"""Regression test for gh-3971: ``_setup_server`` TOCTOU race.

Before the fix, ``Dash._setup_server`` set its guard flag before doing the
work that flag protects (populating ``registered_paths``, ``callback_map``,
etc.). Under a multi-threaded WSGI worker such as ``gunicorn -k gthread``,
a second thread arriving mid-setup could observe the flag already set, skip
setup, and then read ``registered_paths`` while it was still empty, which
caused component-bundle requests to 500 with "Error loading dependency."

The test simulates a concurrent second request by slowing down one of the
inner setup steps and having several threads call ``_setup_server`` at the
same time. After every thread returns, ``registered_paths`` must be
populated, because a return from ``_setup_server`` is meant to guarantee
the setup work is done.
"""
import threading
import time

from dash import Dash, html


def test_setup_server_is_atomic_under_concurrent_requests():
    app = Dash()
    app.layout = html.Div(id="root")

    original_generate_scripts_html = app._generate_scripts_html

    def slow_generate_scripts_html():
        # Widen the TOCTOU window so a stock CPython scheduler reliably lets
        # other threads reach the guard while this one is still running.
        time.sleep(0.1)
        return original_generate_scripts_html()

    app._generate_scripts_html = slow_generate_scripts_html

    thread_count = 4
    barrier = threading.Barrier(thread_count)
    paths_seen_after_setup = []
    lock = threading.Lock()

    def worker():
        barrier.wait()
        app._setup_server()
        with lock:
            paths_seen_after_setup.append(set(app.registered_paths))

    threads = [threading.Thread(target=worker) for _ in range(thread_count)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(paths_seen_after_setup) == thread_count
    for paths in paths_seen_after_setup:
        # Every thread that received control back from _setup_server must
        # observe registered_paths already populated by the winning thread.
        # Before the fix, threads that raced past the guard saw an empty set.
        assert paths, (
            "A thread returned from _setup_server before the setup work "
            "was done; registered_paths was still empty."
        )
