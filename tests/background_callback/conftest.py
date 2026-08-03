import os

import pytest

if "REDIS_URL" in os.environ:
    managers = ["celery-filesystem", "celery-redis", "diskcache"]
else:
    print("Skipping celery tests on Redis because REDIS_URL is not defined")
    managers = ["celery-filesystem", "diskcache"]


@pytest.fixture(params=managers)
def manager(request):
    return request.param
