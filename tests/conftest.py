import os
import sys

import pytest
import dash
from dash._configs import DASH_ENV_VARS


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    # CI safety net for the background/async suites. After pytest has finished
    # and written its reports, those suites can leave non-daemon threads or
    # workers (celery, diskcache, lingering test servers) that keep the
    # interpreter alive at shutdown, wedging the CI step until its job-level
    # timeout even though every test passed. pytest-timeout only bounds
    # individual tests, not this post-session shutdown. When DASH_TEST_FORCE_EXIT
    # is set we hard-exit once the session is done so the step can't hang.
    # Gated by the env var so local runs and other jobs are unaffected; runs
    # trylast so the junit report is already written.
    if os.environ.get("DASH_TEST_FORCE_EXIT"):
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(int(exitstatus))


@pytest.fixture
def empty_environ():
    for k in DASH_ENV_VARS.keys():
        if k in os.environ:
            os.environ.pop(k)


@pytest.fixture
def clear_pages_state():
    init_pages_state()
    yield
    init_pages_state()


def init_pages_state():
    """Clear all global state that is used by pages feature."""
    dash._pages.PAGE_REGISTRY.clear()
    dash._pages.CONFIG.clear()
    dash._pages.CONFIG.__dict__.clear()
