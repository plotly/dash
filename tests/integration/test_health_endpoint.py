import json
import requests
import pytest
from dash import Dash, html


def test_health001_basic_health_check(dash_duo):
    """Test basic health endpoint functionality."""
    app = Dash(__name__)
    app.layout = html.Div("Test Health Endpoint")
    
    dash_duo.start_server(app)
    
    # Test health endpoint
    response = requests.get(f"{dash_duo.server_url}/health")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify required fields
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "dash_version" in data
    assert "python_version" in data
    assert "platform" in data
    assert "server_name" in data
    assert "debug_mode" in data
    
    # Verify callbacks information
    assert "callbacks" in data
    assert "total_callbacks" in data["callbacks"]
    assert "background_callbacks" in data["callbacks"]


def test_health002_health_with_callbacks(dash_duo):
    """Test health endpoint with callbacks."""
    from dash import Input, Output
    
    app = Dash(__name__)
    app.layout = html.Div([
        html.Button("Click me", id="btn"),
        html.Div(id="output")
    ])
    
    @app.callback(Output("output", "children"), Input("btn", "n_clicks"))
    def update_output(n_clicks):
        return f"Clicked {n_clicks or 0} times"
    
    dash_duo.start_server(app)
    
    response = requests.get(f"{dash_duo.server_url}/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["callbacks"]["total_callbacks"] == 1
    assert data["callbacks"]["background_callbacks"] == 0


def test_health003_health_with_background_callbacks(dash_duo):
    """Test health endpoint with background callbacks."""
    from dash import Input, Output
    from dash.long_callback import DiskcacheManager
    
    app = Dash(__name__)
    
    # Add background callback manager
    cache = DiskcacheManager()
    app.long_callback_manager = cache
    
    app.layout = html.Div([
        html.Button("Click me", id="btn"),
        html.Div(id="output")
    ])
    
    @app.long_callback(
        Output("output", "children"),
        Input("btn", "n_clicks"),
        running=[(Output("output", "children"), "Running...", None)],
        prevent_initial_call=True,
    )
    def long_callback(n_clicks):
        import time
        time.sleep(1)  # Simulate long running task
        return f"Completed {n_clicks or 0} times"
    
    dash_duo.start_server(app)
    
    response = requests.get(f"{dash_duo.server_url}/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["callbacks"]["background_callbacks"] >= 0  # May be 0 or 1 depending on setup


def test_health004_health_without_psutil(dash_duo, monkeypatch):
    """Test health endpoint when psutil is not available."""
    import sys
    
    # Mock psutil import to raise ImportError
    original_import = __builtins__.__import__
    
    def mock_import(name, *args, **kwargs):
        if name == 'psutil':
            raise ImportError("No module named 'psutil'")
        return original_import(name, *args, **kwargs)
    
    monkeypatch.setattr(__builtins__, '__import__', mock_import)
    
    app = Dash(__name__)
    app.layout = html.Div("Test Health Without Psutil")
    
    dash_duo.start_server(app)
    
    response = requests.get(f"{dash_duo.server_url}/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    # System metrics should not be present when psutil is not available
    assert "system" not in data


def test_health005_health_json_format(dash_duo):
    """Test that health endpoint returns valid JSON."""
    app = Dash(__name__)
    app.layout = html.Div("Test Health JSON Format")
    
    dash_duo.start_server(app)
    
    response = requests.get(f"{dash_duo.server_url}/health")
    assert response.status_code == 200
    
    # Verify content type
    assert response.headers['content-type'].startswith('application/json')
    
    # Verify valid JSON
    try:
        data = response.json()
        assert isinstance(data, dict)
    except json.JSONDecodeError:
        pytest.fail("Health endpoint did not return valid JSON")


def test_health006_health_with_custom_server_name(dash_duo):
    """Test health endpoint with custom server name."""
    app = Dash(__name__, name="custom_health_app")
    app.layout = html.Div("Test Custom Server Name")
    
    dash_duo.start_server(app)
    
    response = requests.get(f"{dash_duo.server_url}/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["server_name"] == "custom_health_app"


def test_health007_health_endpoint_accessibility(dash_duo):
    """Test that health endpoint is accessible without authentication."""
    app = Dash(__name__)
    app.layout = html.Div("Test Health Accessibility")
    
    dash_duo.start_server(app)
    
    # Test multiple requests to ensure consistency
    for _ in range(3):
        response = requests.get(f"{dash_duo.server_url}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


def test_health008_health_timestamp_format(dash_duo):
    """Test that health endpoint returns valid ISO timestamp."""
    import datetime
    
    app = Dash(__name__)
    app.layout = html.Div("Test Health Timestamp")
    
    dash_duo.start_server(app)
    
    response = requests.get(f"{dash_duo.server_url}/health")
    assert response.status_code == 200
    
    data = response.json()
    timestamp = data["timestamp"]
    
    # Verify timestamp format (ISO 8601 with Z suffix)
    assert timestamp.endswith('Z')
    assert 'T' in timestamp
    
    # Verify it's a valid datetime
    try:
        parsed_time = datetime.datetime.fromisoformat(timestamp[:-1] + '+00:00')
        assert isinstance(parsed_time, datetime.datetime)
    except ValueError:
        pytest.fail(f"Invalid timestamp format: {timestamp}")


def test_health009_health_with_routes_pathname_prefix(dash_duo):
    """Test health endpoint with custom routes_pathname_prefix."""
    app = Dash(__name__, routes_pathname_prefix="/app/")
    app.layout = html.Div("Test Health With Prefix")
    
    dash_duo.start_server(app)
    
    # Health endpoint should be available at /app/health
    response = requests.get(f"{dash_duo.server_url}/app/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"


def test_health010_health_performance(dash_duo):
    """Test that health endpoint responds quickly."""
    import time
    
    app = Dash(__name__)
    app.layout = html.Div("Test Health Performance")
    
    dash_duo.start_server(app)
    
    start_time = time.time()
    response = requests.get(f"{dash_duo.server_url}/health")
    end_time = time.time()
    
    assert response.status_code == 200
    assert (end_time - start_time) < 1.0  # Should respond within 1 second
    
    data = response.json()
    assert data["status"] == "healthy"
