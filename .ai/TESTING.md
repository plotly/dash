# Testing

Dash includes a pytest/Selenium testing framework for unit and integration tests. Located in `dash/testing/`.

## Quick Start

```bash
# Install testing dependencies
pip install -e .[testing]

# Run all tests
pytest tests/

# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run specific test
pytest tests/integration/callbacks/test_basic.py::test_name

# Headless mode (CI)
pytest --headless tests/integration/
```

## Fixtures

The main fixture is `dash_duo` - a composite of server + browser:

```python
def test_basic_callback(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div([
        html.Button("Click", id="btn", n_clicks=0),
        html.Div(id="output")
    ])

    @app.callback(Output("output", "children"), Input("btn", "n_clicks"))
    def update(n):
        return f"Clicked {n} times"

    dash_duo.start_server(app)
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "Clicked 1 times")
```

### Available Fixtures

| Fixture | Description |
|---------|-------------|
| `dash_duo` | Threaded server + browser (default for integration tests) |
| `dash_duo_mp` | Multi-process server + browser |
| `dash_br` | Browser only (no server) |
| `dash_thread_server` | Threaded server only |
| `dash_process_server` | Process-based server only |
| `dashr` | DashR server + browser |
| `dashjl` | Dash.jl server + browser |

## Browser Methods

### Element Selection

```python
dash_duo.find_element("#my-id")           # Single element by CSS selector
dash_duo.find_elements(".my-class")       # All matching elements
dash_duo.wait_for_element("#loading")     # Wait for element to appear
dash_duo.wait_for_element_by_id("output") # Wait by ID
```

### Wait Conditions

```python
# Wait for exact text
dash_duo.wait_for_text_to_equal("#output", "Expected text")

# Wait for text containing substring
dash_duo.wait_for_contains_text("#output", "partial")

# Wait for CSS class
dash_duo.wait_for_class_to_equal("#elem", "active")
dash_duo.wait_for_contains_class("#elem", "loading")

# Wait for CSS property
dash_duo.wait_for_style_to_equal("#elem", "display", "none")

# Wait for element removal
dash_duo.wait_for_no_elements("#spinner")

# Custom timeout (default 10s)
dash_duo.wait_for_text_to_equal("#slow", "Done", timeout=30)
```

### Interactions

```python
# Click
dash_duo.find_element("#btn").click()
dash_duo.multiple_click("#btn", clicks=5)

# Input
elem = dash_duo.find_element("#input")
elem.send_keys("hello")
dash_duo.clear_input("#input")

# Dropdown
dash_duo.select_dcc_dropdown("#dropdown", value="option1")
dash_duo.select_dcc_dropdown("#dropdown", index=2)

# Graph interactions
dash_duo.click_at_coord_fractions("#graph", 0.5, 0.5)  # Click center
dash_duo.zoom_in_graph_by_ratio("#graph", 0.5, 0.25, 0.5, 0.75)
```

### State Inspection

```python
# Redux state
dash_duo.redux_state_is_loading  # True if callbacks running
dash_duo.redux_state_paths       # Component paths
dash_duo.redux_state_rqs         # Pending requests

# Storage
dash_duo.get_local_storage("store-id")
dash_duo.get_session_storage("session-id")
dash_duo.clear_storage()

# DOM access (BeautifulSoup)
dom = dash_duo.dash_outerhtml_dom
assert dom.find(id="my-component") is not None

# Browser logs (Chrome only)
logs = dash_duo.get_logs()
assert logs == []  # No console errors
```

## Application Runners

Runners manage server lifecycle:

| Runner | How It Works | Use Case |
|--------|--------------|----------|
| `ThreadedRunner` | Daemon thread | Fast, default |
| `ProcessRunner` | Subprocess + waitress | Production-like |
| `MultiProcessRunner` | Multiprocessing | Multi-worker tests |
| `RRunner` | Rscript subprocess | DashR |
| `JuliaRunner` | Julia subprocess | Dash.jl |

```python
def test_with_process_server(dash_process_server):
    app = Dash(__name__)
    app.layout = html.Div("Hello")

    dash_process_server(app)
    response = requests.get(dash_process_server.url)
    assert response.status_code == 200
```

## Wait Utilities

For custom wait conditions (`dash/testing/wait.py`):

```python
from dash.testing.wait import until, until_not

# Poll until condition is True
until(
    lambda: dash_duo.find_element("#status").text == "Ready",
    timeout=10,
    poll=0.5,
    msg="Status never became Ready"
)

# Poll until condition is False
until_not(
    lambda: dash_duo.redux_state_is_loading,
    timeout=5
)
```

## Percy Visual Testing

Percy integration for visual regression testing:

```python
def test_visual_appearance(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div([...])

    dash_duo.start_server(app)

    # Basic snapshot
    dash_duo.percy_snapshot("dashboard-initial")

    # Wait for callbacks before snapshot
    dash_duo.percy_snapshot(
        name="dashboard-loaded",
        wait_for_callbacks=True
    )

    # Convert canvas elements to images (for graphs)
    dash_duo.percy_snapshot(
        name="graph-render",
        convert_canvases=True
    )

    # Responsive widths
    dash_duo.percy_snapshot(
        name="responsive",
        widths=[375, 768, 1280]
    )
```

Navigate and snapshot in one call:

```python
dash_duo.visit_and_snapshot(
    resource_path="/page2",
    hook_id="page2-content",
    wait_for_callbacks=True
)
```

## CLI Options

```bash
# Browser selection
pytest --webdriver Chrome      # Default
pytest --webdriver Firefox

# Headless mode
pytest --headless

# Selenium Grid
pytest --remote --remote-url http://grid:4444/wd/hub

# Percy
pytest --percy-assets tests/assets
pytest --nopercyfinalize       # Don't finalize Percy build

# Debugging
pytest --pause                 # Pause with pdb after page load
```

## Test Organization

```
tests/                                    # Core Dash tests
├── unit/                                 # Fast tests, no browser
├── integration/                          # Browser-based tests
│   ├── callbacks/                        # Callback behavior
│   ├── clientside/                       # Clientside callbacks
│   ├── dash/                             # Core app features
│   ├── dash_assets/                      # Asset loading
│   ├── devtools/                         # Dev tools UI
│   ├── multi_page/                       # Pages system
│   ├── renderer/                         # Frontend rendering
│   └── security/                         # Security features
├── async_tests/                          # Async callback tests
├── background_callback/                  # Background callback tests
├── backend_tests/                        # Server-side tests
└── compliance/                           # Type checking compliance
    └── test_typing.py                    # pyright/mypy validation

components/dash-core-components/tests/    # DCC component tests
├── unit/                                 # Unit tests
└── integration/                          # Per-component browser tests
    ├── dropdown/
    ├── graph/
    ├── input/
    ├── slider/
    ├── store/
    ├── upload/
    └── ...

components/dash-html-components/tests/    # HTML component tests
├── test_dash_html_components.py
├── test_div_tabIndex.py
└── test_integration.py

components/dash-table/tests/              # DataTable tests
├── unit/                                 # Python unit tests
├── js-unit/                              # JavaScript unit tests
├── selenium/                             # Browser tests
└── visual/                               # Visual regression tests

dash/dash-renderer/tests/                 # Renderer JS tests
├── isAppReady.test.js
└── persistence.test.js
```

### Running Component Tests

```bash
# DCC tests
pytest components/dash-core-components/tests/

# Specific DCC component
pytest components/dash-core-components/tests/integration/dropdown/

# HTML components
pytest components/dash-html-components/tests/

# DataTable
pytest components/dash-table/tests/selenium/

# Renderer JS tests
cd dash/dash-renderer && npm test
```

## Type Checking Compliance

The `tests/compliance/test_typing.py` tests validate that Dash code passes static type checkers (pyright, mypy). This ensures type annotations are correct and users get proper IDE support.

### What It Tests

1. **Component prop types** - Validates generated TypeScript component types work correctly:
   ```python
   # Should pass - correct type
   TypeScriptComponent(a_string='hello')

   # Should fail - wrong type
   TypeScriptComponent(a_string=123)  # Expected str, got int
   ```

2. **Layout types** - Validates layout accepts correct children types:
   ```python
   # Valid - components, strings, numbers
   html.Div([html.H2('Title'), 'text', 123])

   # Invalid - dict in children
   html.Div([{'invalid': 'dict'}])
   ```

3. **Callback return types** - Validates callback returns match Output type:
   ```python
   @callback(Output("out", "children"), Input("in", "value"))
   def update() -> html.Div:
       return html.Div('Valid')  # OK
       return []                  # Type error
   ```

### Running Type Checks

```bash
# Run compliance tests
pytest tests/compliance/

# Run pyright directly
pyright dash/

# Run mypy directly (Python 3.10+)
mypy dash/
```

### Type Checkers Used

| Checker | Python Version | Notes |
|---------|---------------|-------|
| pyright | All | Primary checker, always runs |
| mypy | 3.10+ | Runs on Python 3.10 and above |

## Common Patterns

### Testing Callbacks

```python
def test_callback_updates_output(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div([
        dcc.Input(id="input", value=""),
        html.Div(id="output")
    ])

    @app.callback(Output("output", "children"), Input("input", "value"))
    def update(value):
        return f"You typed: {value}"

    dash_duo.start_server(app)

    input_elem = dash_duo.find_element("#input")
    input_elem.send_keys("hello")

    dash_duo.wait_for_text_to_equal("#output", "You typed: hello")
    assert dash_duo.get_logs() == []
```

### Testing Loading States

```python
def test_loading_indicator(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div([
        html.Button("Load", id="btn"),
        dcc.Loading(html.Div(id="output"))
    ])

    @app.callback(Output("output", "children"), Input("btn", "n_clicks"))
    def slow_update(n):
        time.sleep(1)
        return "Loaded"

    dash_duo.start_server(app)
    dash_duo.find_element("#btn").click()

    # Verify loading state appears
    dash_duo.wait_for_element(".dash-spinner")

    # Then verify it completes
    dash_duo.wait_for_text_to_equal("#output", "Loaded")
    dash_duo.wait_for_no_elements(".dash-spinner")
```

### Testing Background Callbacks

```python
def test_background_callback(dash_duo, diskcache_manager):
    app = Dash(__name__)
    app.layout = html.Div([
        html.Button("Start", id="btn"),
        html.Div(id="progress"),
        html.Div(id="result")
    ])

    @app.callback(
        Output("result", "children"),
        Input("btn", "n_clicks"),
        progress=Output("progress", "children"),
        background=True,
        manager=diskcache_manager,
    )
    def compute(set_progress, n):
        for i in range(5):
            set_progress(f"{i*20}%")
            time.sleep(0.1)
        return "Done"

    dash_duo.start_server(app)
    dash_duo.find_element("#btn").click()

    dash_duo.wait_for_contains_text("#progress", "%")
    dash_duo.wait_for_text_to_equal("#result", "Done")
```

### Testing Multi-Page Apps

```python
def test_page_navigation(dash_duo):
    app = Dash(__name__, use_pages=True)
    # pages/ directory contains page modules

    dash_duo.start_server(app)

    # Test home page
    dash_duo.wait_for_element("#home-content")

    # Navigate to another page
    dash_duo.find_element('a[href="/about"]').click()
    dash_duo.wait_for_element("#about-content")

    # Check URL updated
    assert "/about" in dash_duo.driver.current_url
```

## Key Files

| File | Purpose |
|------|---------|
| `dash/testing/plugin.py` | Pytest plugin, fixture definitions |
| `dash/testing/browser.py` | Browser class with Selenium wrapper |
| `dash/testing/composite.py` | DashComposite (server + browser) |
| `dash/testing/application_runners.py` | Server runners |
| `dash/testing/wait.py` | Wait utilities and conditions |
| `dash/testing/dash_page.py` | Redux state access mixin |
| `dash/testing/errors.py` | Custom exceptions |

## Errors

```python
from dash.testing.errors import (
    TestingTimeoutError,      # Wait condition timed out
    DashAppLoadingError,      # App failed to load
    ServerCloseError,         # Server didn't stop cleanly
    BrowserError,             # Browser/WebDriver issue
)
```
