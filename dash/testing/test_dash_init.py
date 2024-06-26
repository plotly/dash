from dash import Dash
import pytest


def test_dash_init_with_defaults():
    """Test that default initialization works."""
    app = Dash()
    assert app.name == "__main__", "Default app name should be __main__"
    assert app.server, "Default app should have a server instance"


def test_dash_init_with_custom_parameters():
    """Test that custom parameters are correctly assigned."""
    app = Dash(name="test_app", assets_folder="test_assets")
    assert app.name == "test_app", "App name should be set to 'test_app'"
    assert app.assets_folder == "test_assets", "Assets folder should be 'test_assets'"
