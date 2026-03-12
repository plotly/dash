import os

import psutil
import pytest


if "REDIS_URL" in os.environ:
    managers = ["celery", "diskcache"]
else:
    print("Skipping celery tests because REDIS_URL is not defined")
    managers = ["diskcache"]


@pytest.fixture(params=managers)
def manager(request):
    return request.param


@pytest.fixture(scope="session", autouse=True)
def cleanup_background_processes():
    """Ensure all background processes are cleaned up when tests finish."""
    yield
    # Kill any remaining celery workers
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cmdline = proc.info.get("cmdline") or []
            cmdline_str = " ".join(cmdline) if cmdline else ""
            if "celery" in cmdline_str and "worker" in cmdline_str:
                proc.kill()
                proc.wait(timeout=3)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            pass
