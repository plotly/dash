import os

import pytest


if "REDIS_URL" in os.environ:
    managers = ["celery", "diskcache"]
else:
    print("Skipping celery tests because REDIS_URL is not defined")
    managers = ["diskcache"]


@pytest.fixture(params=managers)
def manager(request):
    return request.param
