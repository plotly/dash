import subprocess
import sys
import time
from typing import List
import socket
from pathlib import Path

import requests
import pytest


# This is the content of the dummy Dash app we'll create for the test.
APP_CONTENT = """
from dash import Dash, html

# The unique string we will check for in the test
CUSTOM_INDEX_STRING = "Hello Dash CLI Test World"

app = Dash(__name__)

# Override the default index HTML to include our custom string
app.index_string = f'''
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%css%}}
    </head>
    <body>
        <h1>{CUSTOM_INDEX_STRING}</h1>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
'''

app.layout = html.Div("This is the app layout.")
"""


# Helper function to find an available network port
def find_free_port():
    """Finds a free port on the local machine."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.mark.parametrize("app_path", ["app:app", "app"])
@pytest.mark.parametrize("cmd", [[sys.executable, "-m", "dash"], ["plotly"]])
def test_run_command_serves_app(tmp_path: Path, app_path: str, cmd: List[str]):
    """
    Tests that the `run` command successfully serves a Dash app.
    """
    # 1. Setup: Create the app in a temporary directory
    app_dir = tmp_path / "my_test_app"
    app_dir.mkdir()
    (app_dir / "app.py").write_text(APP_CONTENT)

    port = find_free_port()
    url = f"http://127.0.0.1:{port}"

    # Command to execute. We run the cli.py script directly with the python
    # interpreter that is running pytest. This is more robust than assuming
    # an entry point is on the PATH.
    command = [
        *cmd,
        "run",
        str(app_path),
        "--port",
        str(port),
    ]

    process = None
    try:
        # 2. Execution: Start the CLI command as a background process
        # The working directory `cwd` is crucial so that "import app" works.
        process = subprocess.Popen(  # pylint: disable=consider-using-with
            command,
            cwd=str(app_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Give the server a moment to start up.
        time.sleep(3)

        # Check if the process terminated unexpectedly
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            pytest.fail(
                f"The CLI process terminated prematurely.\n"
                f"Exit Code: {process.returncode}\n"
                f"STDOUT:\n{stdout}\n"
                f"STDERR:\n{stderr}"
            )

        # 3. Verification: Make a request to the running server
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Check for HTTP errors like 404 or 500

        # 4. Assertion: Check for the custom content from the app
        assert "Hello Dash CLI Test World" in response.text
        print(f"\nSuccessfully fetched app from {url}")

    finally:
        # 5. Teardown: Ensure the server process is always terminated
        if process:
            print(f"\nTerminating server process (PID: {process.pid})")
            process.terminate()
            # Use communicate() to wait for process to die and get output
            try:
                stdout, stderr = process.communicate(timeout=5)
                print(f"Server process STDOUT:\n{stdout}")
                print(f"Server process STDERR:\n{stderr}")
            except subprocess.TimeoutExpired:
                print("Process did not terminate gracefully, killing.")
                process.kill()
