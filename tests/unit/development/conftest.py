import json
import os
from collections import OrderedDict

import pytest

from . import _dir


@pytest.fixture
def load_test_metadata_json():
    json_path = os.path.join(_dir, "metadata_test.json")
    with open(json_path) as data_file:
        json_string = data_file.read()
        data = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(json_string)
    return data
