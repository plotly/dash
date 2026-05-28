# Architecture

## Python Backend Framework

- **`dash/dash.py`** - Main `Dash` application class (~2000 lines). Orchestrates the server backend, layout management, callback registration, routing, and asset serving. Key methods: `layout` property, `callback()`, `clientside_callback()`, `run()`.

- **`dash/backends/`** - Server backend implementations. See [Server Backends](#server-backends) section for details.

- **`dash/_callback.py`** - Callback registration and execution. Contains `callback()` decorator (usable as `@dash.callback` without app instance), `clientside_callback()`, and `register_callback()` which inserts callbacks into the callback map.

- **`dash/dependencies.py`** - Dependency classes for callbacks:
  - `Input` - Triggers callback when value changes
  - `Output` - Component property to update (supports `allow_duplicate=True`)
  - `State` - Read value without triggering callback
  - `ClientsideFunction` - Reference to JS function for clientside callbacks
  - Wildcards: `MATCH`, `ALL`, `ALLSMALLER` for pattern-matching IDs

- **`dash/development/base_component.py`** - `Component` base class with `ComponentMeta` metaclass. All Dash components inherit from this. Components auto-register in `ComponentRegistry` and serialize to JSON via `to_plotly_json()`.

- **`dash/_pages.py`** - Multi-page app support. `PAGE_REGISTRY` holds registered pages, `register_page()` decorator registers page modules with routes.

## Layout System

The layout defines the UI as a tree of components:

```python
app.layout = html.Div([
    dcc.Input(id='input', value='initial'),
    html.Div(id='output')
])
```

- **Static layout**: Assigned directly as a component tree
- **Dynamic layout**: Assigned as a function that returns components (called on each page load, useful for per-session state)
- Layout is serialized to JSON and sent to the React frontend via `/_dash-layout`
- Components can contain other components via `children` prop
- Component IDs can be strings or dicts (for pattern-matching callbacks)

## Callback Types

### 1. Regular Callbacks

`@app.callback` or `@dash.callback`:

```python
@app.callback(Output('output', 'children'), Input('input', 'value'))
def update(value):
    return f'You entered: {value}'
```

Server-side Python function called when inputs change. Outputs update component properties.

### 2. Clientside Callbacks

`app.clientside_callback`:

```python
app.clientside_callback(
    """function(value) { return 'You entered: ' + value; }""",
    Output('output', 'children'),
    Input('input', 'value')
)
```

JavaScript function runs in browser. Faster for simple transformations, no server round-trip. Can reference `window.dash_clientside.namespace.function_name` or inline JS string.

### 3. Background Callbacks

`background=True`:

```python
@app.callback(Output('output', 'children'), Input('btn', 'n_clicks'),
              background=True, manager=diskcache_manager,
              running=[(Output('btn', 'disabled'), True, False)],
              progress=[Output('progress', 'value')])
def compute(set_progress, n_clicks):
    for i in range(10):
        set_progress(i * 10)
        time.sleep(1)
    return 'Done'
```

Callbacks executed in separate process via Celery or Diskcache manager. Supports `progress` updates, `running` state changes, and `cancel` inputs. See [Background Callbacks](#background-callbacks) section for details.

### 4. Pattern-Matching Callbacks

```python
@app.callback(
    Output({'type': 'output', 'index': MATCH}, 'children'),
    Input({'type': 'input', 'index': MATCH}, 'value')
)
def update(value):
    return value
```

Use dict IDs with wildcards (`MATCH`, `ALL`, `ALLSMALLER`) to target dynamically-generated components.

## Server Routes

- `/_dash-layout` - Returns initial component tree as JSON
- `/_dash-dependencies` - Returns callback definitions
- `/_dash-update-component` - Executes callbacks, returns updated props
- `/_dash-component-suites/<package>/<path>` - Serves component JS/CSS assets
- `/assets/<path>` - Serves static assets from app's assets folder

## Server Backends

Dash supports multiple web server backends. The backend abstraction is in `dash/backends/`.

### Available Backends

| Backend | Type | Install | Use Case |
|---------|------|---------|----------|
| **Flask** (default) | WSGI (sync) | `pip install dash` | Standard deployments, simplicity |
| **Quart** | ASGI (async) | `pip install dash[quart]` | Async callbacks, WebSocket support |
| **FastAPI** | ASGI (async) | `pip install dash[fastapi]` | OpenAPI docs, async, modern Python |

### Usage

**Default (Flask):**
```python
from dash import Dash
app = Dash(__name__)
```

**With existing server instance:**
```python
from flask import Flask
from dash import Dash

server = Flask(__name__)
app = Dash(__name__, server=server)
```

**Quart backend:**
```python
from quart import Quart
from dash import Dash

server = Quart(__name__)
app = Dash(__name__, server=server)
```

**FastAPI backend:**
```python
from fastapi import FastAPI
from dash import Dash

server = FastAPI()
app = Dash(__name__, server=server)

# Run with: uvicorn module:app.server --reload
```

### Architecture

The backend system uses an abstract interface:

- **`BaseDashServer`** (`dash/backends/base_server.py`) - Abstract base class defining the server interface. All backends implement this.

- **`RequestAdapter`** - Normalizes HTTP request objects across frameworks. Provides unified access to `args`, `cookies`, `headers`, `get_json()`, etc.

- **`ResponseAdapter`** - Normalizes response creation. Handles `set_cookie()`, `set_header()`, `set_response()`.

- **`get_backend(name)`** - Factory function to get backend class by name (`"flask"`, `"quart"`, `"fastapi"`).

- **`get_server_type(server)`** - Auto-detects backend from a server instance.

### Backend Implementations

**Flask** (`dash/backends/_flask.py`):
- `FlaskDashServer` - Wraps Flask app
- `FlaskRequestAdapter` - Uses `flask.request` proxy
- `FlaskResponseAdapter` - Uses `flask.Response`
- Compression via `flask-compress`

**Quart** (`dash/backends/_quart.py`):
- `QuartDashServer` - Wraps Quart app (async Flask API)
- `QuartRequestAdapter` - Uses `quart.request` proxy
- `QuartResponseAdapter` - Uses `quart.Response`
- All route handlers are `async def`
- Compression via `quart-compress`

**FastAPI** (`dash/backends/_fastapi.py`):
- `FastAPIDashServer` - Wraps FastAPI app
- `FastAPIRequestAdapter` - Uses context variable for current request
- `FastAPIResponseAdapter` - Uses Starlette responses
- `DashMiddleware` - Consolidated ASGI middleware for request handling
- Runs with uvicorn, supports hot reload
- Built-in GZip compression

### Key Interface Methods

All backends implement:

```python
class BaseDashServer(ABC):
    def create_app(name, config) -> server        # Create new server
    def add_url_rule(rule, view_func, ...)        # Register routes
    def before_request(func)                       # Request hooks
    def after_request(func)                        # Response hooks
    def run(dash_app, host, port, debug)          # Start dev server
    def make_response(data, mimetype, status)     # Create response
    def jsonify(obj)                              # JSON response
    def setup_index(dash_app)                     # Register / route
    def serve_callback(dash_app)                  # Callback endpoint
    def setup_component_suites(dash_app)          # JS/CSS serving
```

### Accessing the Backend

```python
app = Dash(__name__)

# Get the underlying server
app.server          # Flask/Quart/FastAPI instance

# Get the backend wrapper
app.backend         # BaseDashServer subclass instance
app.backend.server_type  # "flask", "quart", or "fastapi"

# Access request in callbacks
from dash import dash
dash.get_app().backend.request_adapter()  # RequestAdapter instance
```

## Frontend (dash-renderer)

**`dash/dash-renderer/src/`** contains the TypeScript/React frontend. See [RENDERER.md](RENDERER.md) for detailed documentation on:

- Layout traversal (`crawlLayout`) and `children_props`
- Component resolution from `window[namespace][type]`
- Callback triggering via `setProps` and `notifyObservers`
- Redux store structure (layout, paths, callbacks, graphs)
- Observer system for callback processing
- `window.dash_clientside` API
- `window.dash_component_api` API

### React Version

Dash supports multiple React versions. Configured in `dash/_dash_renderer.py`.

**Available versions:** 18.3.1 (default), 18.2.0, 16.14.0

Set via environment variable (experimental):

```bash
REACT_VERSION=16.14.0 python app.py
```

Or programmatically before creating the app:

```python
from dash._dash_renderer import _set_react_version
_set_react_version("16.14.0")

from dash import Dash
app = Dash(__name__)
```

This is useful for compatibility with older component libraries that require React 16.

## Pages System

Multi-page apps use `dash/_pages.py` with automatic routing via `dcc.Location`.

### Page Registration

Each page module calls `register_page()`:

```python
# pages/analytics.py
from dash import register_page, html

register_page(__name__)  # infers path /analytics from module name

layout = html.Div("Analytics page")
```

- **`PAGE_REGISTRY`** - `OrderedDict` storing all registered pages with metadata
- **`register_page(module, path=None, ...)`** - Registers page with inferred or explicit path, title, description, image

### Page Container

When `use_pages=True`, Dash injects `page_container` as the layout (`dash/dash.py:148-158`):

```python
page_container = html.Div([
    dcc.Location(id="_pages_location", refresh="callback-nav"),
    html.Div(id="_pages_content"),      # current page layout injected here
    dcc.Store(id="_pages_store"),       # stores page title/metadata
])
```

### Routing Mechanism

1. `dcc.Location` tracks browser URL changes
2. Internal callback listens to `pathname` and `search` inputs
3. `_path_to_page()` matches URL to registered page in `PAGE_REGISTRY`
4. Page layout injected into `_pages_content` div

### Path Templates (Dynamic Routes)

Pages can capture URL variables:

```python
register_page(__name__, path_template="/asset/<asset_id>")

def layout(asset_id=None):
    return html.Div(f"Asset: {asset_id}")
```

`_parse_path_variables()` extracts variables via regex and passes them as kwargs to the layout function.

### Auto-Discovery

`_import_layouts_from_pages()` walks the `pages/` folder:
- Skips files starting with `_` or `.`
- Only imports `.py` files containing `register_page`
- Auto-assigns `layout` attribute from each module to the registry

### Page Ordering

Pages sorted by: numeric `order` → string `order` → no order → module name. Home page (`/`) defaults to order `0`.

## Assets and Static Files

### Asset Directory

The `assets/` folder is automatically scanned at startup (`dash/dash.py:_walk_assets_directory`):

- `.css` files → appended to stylesheets
- `.js` files → appended to scripts
- `favicon.ico` → used as app favicon
- Files matching `assets_ignore` regex are skipped

### Loading Order

Resources load in this order (`dash/dash.py:1127-1165`):

1. React dependencies (from dash-renderer)
2. Component library scripts (dash-html-components, dash-core-components, etc.)
3. External scripts (`external_scripts` parameter)
4. Dash renderer bundle
5. Clientside callback scripts (inline)

CSS follows similar ordering with external stylesheets first.

### Fingerprinting and Caching

Component assets use fingerprinted URLs for cache busting (`dash/fingerprint.py`):

```
/_dash-component-suites/dash_core_components/dash_core_components.v2_14_0m1699900000.min.js
```

- Fingerprinted resources: 1-year cache header
- Non-fingerprinted: ETag validation
- Asset files: query string `?m={modification_time}`

### Configuration Options

```python
Dash(
    assets_folder='assets',           # path to assets directory
    assets_url_path='assets',         # URL path segment
    assets_ignore='.*ignored.*',      # regex to skip files
    assets_external_path=None,        # CDN base URL for assets
    serve_locally=True,               # True=local files, False=CDN
    external_scripts=[],              # additional JS URLs
    external_stylesheets=[],          # additional CSS URLs
)
```

### Asset URL Generation

`app.get_asset_url(path)` returns the correct URL accounting for `requests_pathname_prefix` (important for Dash Enterprise deployments where apps have URL prefixes).

## Error Handling

### Debug Mode

Debug mode enables developer tools (`dash/dash.py:_setup_dev_tools`):

```python
app.run(debug=True)
# Or via environment: DASH_DEBUG=true
```

### Dev Tools Options

```python
app.enable_dev_tools(
    dev_tools_ui=True,              # show error UI overlay
    dev_tools_props_check=True,     # validate component prop types
    dev_tools_serve_dev_bundles=True,  # use development JS (better errors)
    dev_tools_hot_reload=True,      # auto-reload on file changes
    dev_tools_prune_errors=True,    # strip internal frames from tracebacks
)
```

Environment variables: `DASH_DEBUG`, `DASH_UI`, `DASH_PROPS_CHECK`, `DASH_HOT_RELOAD`, etc.

### Callback Exceptions

**`PreventUpdate`** - Skip updating outputs without error:

```python
from dash.exceptions import PreventUpdate

@app.callback(Output('out', 'children'), Input('in', 'value'))
def update(value):
    if not value:
        raise PreventUpdate
    return value
```

**`no_update`** - Skip specific outputs in multi-output callbacks:

```python
from dash import no_update

@app.callback(Output('a', 'children'), Output('b', 'children'), Input('in', 'value'))
def update(value):
    return value, no_update  # only updates 'a'
```

### Error Handlers

Callbacks support `on_error` for custom error handling:

```python
def handle_error(err):
    logging.error(f"Callback failed: {err}")
    return "Error occurred"  # returned to output

@app.callback(Output('out', 'children'), Input('in', 'value'), on_error=handle_error)
def update(value):
    return 1 / 0  # triggers error handler
```

App-level error handler set via constructor.

### Validation

- **Layout validation**: When `suppress_callback_exceptions=False` (default), checks that callback IDs exist in layout
- **Callback validation**: `dev_tools_validate_callbacks=True` checks for circular dependencies
- **Props checking**: Validates component prop types against schema in dev mode

### Hot Reload

When enabled, a watch thread monitors:
- `assets/` folder for CSS/JS changes
- Component package directories

Frontend polls `/_reload-hash` and triggers reload when hash changes. Configurable via `hot_reload_interval` (default 3s) and `hot_reload_watch_interval` (default 0.5s).

## Background Callbacks

Background callbacks execute in separate processes, allowing the main server to remain responsive. Managed by `dash/background_callback/managers/`.

### Definition

```python
from dash import callback, Input, Output
from dash.background_callback import DiskcacheManager

cache_manager = DiskcacheManager()

@callback(
    Output("result", "children"),
    Input("button", "n_clicks"),
    background=True,
    manager=cache_manager,
    interval=500,  # polling interval in ms
)
def compute(n_clicks):
    # Expensive computation
    return result
```

### Callback Managers

**`DiskcacheManager`** (`dash/background_callback/managers/diskcache_manager.py`):
- Uses `diskcache.Cache` for persistent storage
- Spawns `multiprocess.Process` for each job
- Results stored on disk, survives server restarts
- Good for single-server deployments

**`CeleryManager`** (`dash/background_callback/managers/celery_manager.py`):
- Requires Celery app with result backend (Redis/RabbitMQ)
- Jobs distributed across Celery workers
- Supports horizontal scaling
- Good for production multi-worker deployments

```python
from celery import Celery
from dash.background_callback import CeleryManager

celery_app = Celery(__name__, broker="redis://localhost:6379/0")
cache_manager = CeleryManager(celery_app)
```

### Progress Updates

The `progress` parameter defines outputs updated during execution:

```python
@callback(
    Output("result", "children"),
    Input("button", "n_clicks"),
    progress=Output("progress-bar", "value"),
    progress_default=0,
    background=True,
    manager=cache_manager,
)
def compute(set_progress, n_clicks):
    for i in range(100):
        set_progress(i)
        time.sleep(0.1)
    return "Complete"
```

- `set_progress` is injected as first argument when `progress` is specified
- Can be single Output or list of Outputs
- `progress_default` sets value when callback not running

### Running State

The `running` parameter updates outputs while the job executes:

```python
@callback(
    Output("result", "children"),
    Input("button", "n_clicks"),
    running=[
        (Output("button", "disabled"), True, False),
        (Output("status", "children"), "Computing...", "Ready"),
    ],
    background=True,
    manager=cache_manager,
)
def compute(n_clicks):
    time.sleep(5)
    return "Done"
```

Each tuple: `(Output, value_while_running, value_when_complete)`

### Cancellation

The `cancel` parameter specifies inputs that abort the job:

```python
@callback(
    Output("result", "children"),
    Input("start-btn", "n_clicks"),
    cancel=[Input("cancel-btn", "n_clicks")],
    background=True,
    manager=cache_manager,
)
def compute(n_clicks):
    # Job terminates if cancel-btn clicked
    return result
```

Managers call `terminate_job()` which kills the process (Diskcache) or revokes the task (Celery).

### Result Caching

Results can be cached to avoid recomputation:

```python
def get_user_id():
    return flask.session.get("user_id")

cache_manager = DiskcacheManager(
    cache_by=[get_user_id],  # cache key includes user ID
    expire=3600,             # TTL in seconds
)
```

- `cache_by` - List of functions whose return values are included in cache key
- `expire` - Time-to-live for cached results
- `cache_args_to_ignore` - Argument indices to exclude from cache key

### How It Works

1. **Initial request**: Frontend triggers callback, backend returns `cacheKey` and `job` ID
2. **Polling**: Frontend polls `/_dash-update-component?cacheKey=...&job=...` at configured interval
3. **Progress**: Each poll returns current progress value if set
4. **Completion**: When job finishes, poll returns final result
5. **Cleanup**: Results cleared from cache (unless `cache_by` specified)

Cache key is SHA256 hash of: function source + arguments + triggered inputs + cache_by values.

### Key Files

- `dash/_callback.py:188-219` - Background spec construction
- `dash/background_callback/managers/__init__.py` - `BaseBackgroundCallbackManager` abstract class
- `dash/background_callback/managers/diskcache_manager.py` - Diskcache implementation
- `dash/background_callback/managers/celery_manager.py` - Celery implementation
- `dash/dash-renderer/src/actions/callbacks.ts:458-685` - Frontend polling logic

## Jupyter Integration

Dash apps can run directly in Jupyter notebooks and JupyterLab. The integration is handled by `dash/_jupyter.py`.

### Display Modes

```python
app.run(
    jupyter_mode="inline",      # Display in notebook cell (default)
    jupyter_width="100%",       # IFrame width
    jupyter_height=650,         # IFrame height in pixels
)
```

| Mode | Behavior |
|------|----------|
| `"inline"` | App displays in notebook cell via IFrame |
| `"external"` | Prints URL, user opens in browser tab |
| `"jupyterlab"` | Opens in dedicated JupyterLab tab |
| `"tab"` | Auto-opens URL in new browser tab |

### How It Works

1. `app.run()` detects Jupyter environment via `get_ipython()`
2. Server starts in background daemon thread
3. Jupyter comm protocol negotiates proxy configuration
4. App displays according to selected mode

```
app.run() in notebook
    ↓
Detect Jupyter → Start server in background thread
    ↓
Comm request → Extension responds with base_url
    ↓
Compute dashboard URL with proxy path
    ↓
Display: IFrame (inline) / URL (external) / Tab (jupyterlab)
```

### Notebook Extension

Classic Jupyter notebooks use `dash/nbextension/`:

- `main.js` - Registers "dash" comm target
- `dash.json` - Extension loader configuration

The extension handles comm messages:
- `base_url_request` → responds with server URL and base path
- Enables proper proxy routing in JupyterHub environments

### JupyterLab Extension

JupyterLab uses `@plotly/dash-jupyterlab/`:

- `src/index.ts` - TypeScript plugin implementing `JupyterFrontEndPlugin`
- `DashIFrameWidget` - Lumino widget for rendering apps in tabs

Handles messages:
- `base_url_request` → responds with JupyterLab server config
- `show` → creates dedicated tab with IFrame widget

Compatible with JupyterLab 2.x, 3.x, and 4.x.

### Proxy Configuration

In JupyterHub/proxy environments, the extension negotiates `requests_pathname_prefix`:

```python
# Computed from Jupyter base path
requests_pathname_prefix = "/user/username/proxy/8050/"
```

This ensures callbacks route correctly through the Jupyter proxy.

### Google Colab

Special handling for Colab:
- Uses `google.colab.output.serve_kernel_port_as_iframe()` for inline
- Uses `google.colab.output.serve_kernel_port_as_window()` for external
- Only supports "inline" and "external" modes

### Key Files

- `dash/_jupyter.py` - `JupyterDash` class, comm handling, server thread
- `dash/nbextension/main.js` - Classic notebook extension
- `@plotly/dash-jupyterlab/src/index.ts` - JupyterLab extension

## Configuration Reference

### Dash() Constructor Parameters

**Basic Setup:**
- `name` - Application name (default: infers from `__name__`)
- `server` - Server instance (Flask, Quart, or FastAPI) or `True` to create Flask (default: `True`)
- `title` - Browser tab title (default: `"Dash"`)
- `update_title` - Title during callbacks (default: `"Updating..."`)

**Assets & Resources:**
- `assets_folder` - Path to assets directory (default: `"assets"`)
- `assets_url_path` - URL path for assets (default: `"assets"`)
- `assets_ignore` - Regex to exclude assets (default: `""`)
- `serve_locally` - Serve from local vs CDN (default: `True`)
- `external_scripts` - Additional JS URLs
- `external_stylesheets` - Additional CSS URLs

**Routing:**
- `url_base_pathname` - Base URL prefix for entire app
- `requests_pathname_prefix` - Prefix for AJAX requests
- `routes_pathname_prefix` - Prefix for API routes

**Multi-Page:**
- `use_pages` - Enable pages system (default: auto-detect)
- `pages_folder` - Path to pages directory (default: `"pages"`)

**Behavior:**
- `suppress_callback_exceptions` - Skip callback validation (default: `False`)
- `prevent_initial_callbacks` - Skip callbacks on load (default: `False`)
- `background_callback_manager` - DiskcacheManager or CeleryManager
- `on_error` - Global callback error handler

**WebSocket Callbacks:**
- `websocket_callbacks` - Enable WebSocket for all callbacks (default: `False`). Requires FastAPI backend.
- `websocket_allowed_origins` - List of allowed origins for WebSocket connections
- `websocket_inactivity_timeout` - Disconnect WebSocket after inactivity period in ms (default: `300000` = 5 minutes). Set to `0` to disable.

### app.run() Parameters

- `host` - Server IP (default: `"127.0.0.1"`, env: `HOST`)
- `port` - Server port (default: `8050`, env: `PORT`)
- `debug` - Enable dev tools (default: `False`, env: `DASH_DEBUG`)
- `jupyter_mode` - Display mode: `"inline"`, `"external"`, `"tab"`

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `DASH_DEBUG` | Enable debug mode |
| `DASH_URL_BASE_PATHNAME` | Base URL prefix |
| `DASH_SUPPRESS_CALLBACK_EXCEPTIONS` | Skip validation |
| `DASH_HOT_RELOAD` | Enable hot reload |
| `DASH_PROPS_CHECK` | Validate prop types |
| `DASH_PRUNE_ERRORS` | Simplify tracebacks |
| `HOST` | Server host |
| `PORT` | Server port |

## Stores and Client-Side State

### dcc.Store

Store data client-side with configurable persistence:

```python
dcc.Store(id='my-store', storage_type='local', data={'key': 'value'})
```

| Storage Type | Persists | Scope | Use Case |
|--------------|----------|-------|----------|
| `'memory'` | Page view only | Tab | Temporary state, debugging |
| `'session'` | Browser session | Tab | Form state, filters |
| `'local'` | Forever | All tabs | User preferences, settings |

**Usage pattern:**
```python
@app.callback(Output('output', 'children'), Input('store', 'data'))
def use_store(data):
    return data['key']

@app.callback(Output('store', 'data'), Input('input', 'value'))
def update_store(value):
    return {'key': value}
```

### Component Persistence

Automatically persist user edits to component props:

```python
dcc.Dropdown(
    id='dropdown',
    options=[...],
    persistence=True,           # Enable persistence
    persistence_type='local',   # local, session, or memory
    persisted_props=['value'],  # Props to persist (default varies by component)
)
```

- **`persistence`** - `True` or unique key to enable
- **`persistence_type`** - Storage backend (default: `'local'`)
- **`persisted_props`** - List of prop names to persist

Supported components: Input, Dropdown, Checklist, RadioItems, Slider, RangeSlider, DatePickerSingle, DatePickerRange, Textarea, Tabs, DataTable.

### When to Use Each

| Need | Solution |
|------|----------|
| Server-controlled state | `dcc.Store` with callbacks |
| Remember user selections | Component `persistence=True` |
| Share state across tabs | `dcc.Store` with `storage_type='local'` |
| Session-only state | `persistence_type='session'` |

## Async Callbacks

Dash supports `async def` callbacks for non-blocking execution.

### Setup

**With Flask backend:**
```bash
pip install dash[async]
```

Async is auto-enabled when `asgiref` is detected. Or explicitly:

```python
app = Dash(__name__, use_async=True)
```

**With Quart or FastAPI backend:** Async is native - no extra dependencies needed.

```python
from fastapi import FastAPI
from dash import Dash

server = FastAPI()
app = Dash(__name__, server=server)  # Async works automatically
```

### Usage

```python
import asyncio

@app.callback(Output('output', 'children'), Input('input', 'value'))
async def async_update(value):
    await asyncio.sleep(1)  # Non-blocking
    return f"Processed: {value}"
```

### Key Points

- Regular async callbacks are **non-blocking** - multiple can run concurrently
- Background callbacks also support `async def`
- Jupyter uses `nest_asyncio` for event loop compatibility
- With Flask backend: requires `dash[async]`, coroutines raise error without it
- With Quart/FastAPI backends: async is native, no extra setup needed

### Async with Background Callbacks

```python
@app.callback(
    Output('result', 'children'),
    Input('btn', 'n_clicks'),
    background=True,
    manager=diskcache_manager,
)
async def async_background(n_clicks):
    await asyncio.sleep(5)
    return "Done"
```

Both DiskcacheManager and CeleryManager support async functions via `asyncio.run()`.

## WebSocket Callbacks

WebSocket callbacks use a persistent WebSocket connection instead of HTTP POST for callback execution. This reduces latency and connection overhead for applications with frequent callbacks.

### Requirements

- **FastAPI backend required**: WebSocket callbacks only work with FastAPI
- **SharedWorker support**: Modern browsers (not IE)

### Usage

**Enable globally for all callbacks:**
```python
from fastapi import FastAPI
from dash import Dash

server = FastAPI()
app = Dash(__name__, server=server, websocket_callbacks=True)
```

**Enable per-callback:**
```python
@app.callback(
    Output('output', 'children'),
    Input('input', 'value'),
    websocket=True  # Use WebSocket for this callback only
)
def update(value):
    return f"Value: {value}"
```

### Configuration

```python
app = Dash(
    __name__,
    server=server,
    websocket_callbacks=True,
    websocket_inactivity_timeout=300000,  # 5 minutes (default)
    websocket_allowed_origins=['https://example.com'],
)
```

- **`websocket_callbacks`** - Enable WebSocket for all callbacks (default: `False`)
- **`websocket_inactivity_timeout`** - Close WebSocket after period of inactivity in milliseconds (default: `300000` = 5 minutes). Heartbeats do not count as activity. Set to `0` to disable timeout. Connection automatically reconnects when needed.
- **`websocket_allowed_origins`** - List of allowed origins for WebSocket connections (security)

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Browser Tab 1                          Browser Tab 2                    │
│ ┌─────────────┐                       ┌─────────────┐                   │
│ │  Renderer   │                       │  Renderer   │                   │
│ └──────┬──────┘                       └──────┬──────┘                   │
│        │ postMessage                         │ postMessage              │
│        └────────────┬───────────────────────┘                           │
│                     ▼                                                   │
│         ┌─────────────────────┐                                         │
│         │    SharedWorker     │  (one per origin)                       │
│         │   dash-ws-worker    │                                         │
│         └──────────┬──────────┘                                         │
└────────────────────│────────────────────────────────────────────────────┘
                     │ WebSocket
                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Server (FastAPI)                                                        │
│   WebSocket Endpoint: /_dash-ws-callback                                │
└─────────────────────────────────────────────────────────────────────────┘
```

**Connection & Reconnection Flow:**
```
Renderer                   SharedWorker                 Server
    │                              │                        │
    │──[CONNECT]──────────────────>│                        │
    │                              │──[WebSocket Connect]──>│
    │<─[CONNECTED]─────────────────│<─[Connected]───────────│
    │                              │                        │
    │──[CALLBACK_REQUEST]─────────>│──[callback request]───>│
    │<─[CALLBACK_RESPONSE]─────────│<─[callback response]───│
    │                              │                        │
    │      (inactivity)            │    (heartbeat check)   │
    │                              │──[close 4001]─────────>│
    │<─[DISCONNECTED]──────────────│                        │
    │                              │                        │
    │──[CALLBACK_REQUEST]─────────>│──[reconnect + send]───>│
    │<─[CALLBACK_RESPONSE]─────────│<─[response]────────────│
```

- **SharedWorker**: Single WebSocket connection shared across browser tabs
- **Heartbeat**: Periodic ping/pong to detect dead connections (30s interval)
- **Inactivity timeout**: Closes connection after no actual callback activity (not heartbeats)
- **Auto-reconnect**: Reconnects automatically when a callback is triggered after timeout

### Long-Running Callbacks with set_props/get_props

WebSocket callbacks can stream updates to the client during execution using `set_props()` and read current component values using `ctx.websocket`:

```python
import asyncio
from dash import callback, Output, Input, set_props, ctx
from dash.exceptions import PreventUpdate

@callback(
    Output('result', 'children'),
    Input('start-btn', 'n_clicks'),
    prevent_initial_call=True
)
async def long_running_task(n_clicks):
    ws = ctx.websocket
    if not ws:
        return "WebSocket not available"

    # Stream progress updates to the client
    for i in range(100):
        # IMPORTANT: Check is_shutdown in loops to detect disconnections
        if ws.is_shutdown:
            raise PreventUpdate  # Exit gracefully on disconnect
        await asyncio.sleep(0.1)
        set_props('progress-bar', {'value': i + 1})
        set_props('status', {'children': f'Processing step {i + 1}/100...'})

    # Read current value from another component
    current_value = await ws.get_prop('input-field', 'value')

    return f"Completed! Input was: {current_value}"
```

**IMPORTANT - Checking `is_shutdown` in Loops:**

Long-running callbacks that use loops **must** check `ws.is_shutdown` to detect when the WebSocket connection has closed. Without this check:
- Callbacks continue running after the client disconnects, wasting server resources
- `set_props` calls go to a closed connection and are lost
- The callback result is never delivered to the client

Only "persistent callbacks" (callbacks with no Output and no Input that use only `set_props`) are automatically restarted when the WebSocket reconnects. Regular callbacks with outputs are not restarted.

**API:**
- `set_props(component_id, props_dict)` - Stream prop updates immediately to client
- `ctx.websocket` - Get WebSocket interface (returns `None` if not in WS context)
- `ws.is_shutdown` - Check if the WebSocket connection has been closed
- `await ws.get_prop(component_id, prop_name)` - Read current prop value from client
- `await ws.set_prop(component_id, prop_name, value)` - Set single prop (async version)
- `await ws.close(code, reason)` - Close the WebSocket connection

### Connection Hooks

Use hooks to validate connections and messages:

```python
from dash import Dash, hooks

@hooks.websocket_connect()
async def validate_connection(websocket):
    """Validate WebSocket connection before accepting."""
    session_id = websocket.cookies.get("session_id")
    if not session_id:
        return (4001, "No session cookie")
    if not await is_valid_session(session_id):
        return (4002, "Invalid session")
    return True  # Allow connection

@hooks.websocket_message()
async def validate_message(websocket, message):
    """Validate each WebSocket message."""
    session_id = websocket.cookies.get("session_id")
    if not await is_session_active(session_id):
        return (4002, "Session expired")
    return True  # Allow message
```

**Hook Return Values:**
- `True` (or truthy) - Allow connection/message
- `False` - Reject with default code (4001)
- `(code, reason)` - Reject with custom close code and reason

### Key Files

- `dash/dash.py` - WebSocket config in `_generate_config()`
- `dash/dash-renderer/src/utils/workerClient.ts` - Browser-side SharedWorker client
- `@plotly/dash-websocket-worker/src/WebSocketManager.ts` - WebSocket connection management
- `@plotly/dash-websocket-worker/src/worker.ts` - SharedWorker entry point
- `dash/backends/_fastapi.py` - Server-side WebSocket handler

## Security

### XSS Protection

Dash automatically sanitizes dangerous URLs in components:

- Blocked protocols: `javascript:`, `vbscript:`
- Protected attributes: `href`, `src`, `action`, `formAction`
- Dangerous URLs replaced with `about:blank`

Components with URL sanitization: `html.A`, `html.Form`, `html.Iframe`, `html.Embed`, `html.Object`, `html.Button`.

### Content Security Policy (CSP)

Generate hashes for inline scripts to use with CSP middleware:

```python
from flask_talisman import Talisman

Talisman(app.server, content_security_policy={
    "default-src": "'self'",
    "script-src": ["'self'"] + app.csp_hashes()
})
```

`app.csp_hashes(hash_algorithm='sha256')` returns base64-encoded hashes.

### Callback Security

- **`suppress_callback_exceptions=False`** (default) - Validates all callback IDs exist in layout
- **`prevent_initial_callbacks=True`** - Prevents callbacks firing on page load (can also set per-callback with `prevent_initial_call`)

### Meta Tag Sanitization

Meta tag values are HTML-escaped to prevent injection:

```python
app = Dash(__name__, meta_tags=[
    {"name": "description", "content": "Safe <content>"}
])
```

### Key Files

- `dash/dash-renderer/src/utils/clientsideFunctions.ts` - URL sanitization (`clean_url`)
- `dash/dash.py:csp_hashes()` - CSP hash generation
- `tests/integration/security/` - Security test coverage
