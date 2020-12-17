# NOTE: this is NOT a pytest test. Just run it as a regular Python script.
# pytest does some magic that makes the issue we're trying to test disappear.

import types
import os

import dash

assert isinstance(dash, types.ModuleType), "dash can be imported"

this_dir = os.path.dirname(__file__)
with open(os.path.join(this_dir, "../../../dash/version.py")) as fp:
    assert dash.__version__ in fp.read(), "version is consistent"

assert getattr(dash, "Dash").__name__ == "Dash", "access to main Dash class is valid"
