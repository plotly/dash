import os

import pytest

os.environ["REDIS_URL"] = "redis://localhost:6379"

if "REDIS_URL" in os.environ:
    managers = ["celery-filesystem", "celery-redis", "diskcache"]
else:
    print("Skipping celery tests because REDIS_URL is not defined")
    managers = ["celery-filesystem", "diskcache"]


@pytest.fixture(params=managers)
def manager(request):
    return request.param
