# Troubleshooting

Common issues and solutions when working with Dash.

## Callback Errors

### "Callback error updating [component]"

**Cause:** Exception raised inside callback function.

**Solution:**
1. Check the terminal for the full traceback
2. Enable debug mode: `app.run(debug=True)`
3. Add error handling:
```python
@app.callback(Output('out', 'children'), Input('in', 'value'), on_error=lambda e: f"Error: {e}")
def update(value):
    ...
```

### "A nonexistent object was used in an `Input`..."

**Cause:** Callback references component ID that doesn't exist in layout.

**Solutions:**
1. Check for typos in component IDs
2. For dynamic layouts, set `suppress_callback_exceptions=True`:
```python
app = Dash(__name__, suppress_callback_exceptions=True)
```
3. Use pattern-matching callbacks for dynamic components

### "Circular dependency detected"

**Cause:** Callback output is also its own input (directly or indirectly).

**Solution:** Restructure callbacks to break the cycle. Use `State` instead of `Input` where possible, or split into multiple callbacks.

### Callback not firing

**Possible causes:**
1. `prevent_initial_call=True` blocking first execution
2. Input component doesn't exist yet (dynamic layout)
3. Component ID mismatch (check spelling, check dict IDs match exactly)

**Debug:** Add `print()` at callback start to verify it's being called.

## Layout Errors

### "Invalid component type"

**Cause:** Passing non-component to layout (e.g., raw dict, unsupported type).

**Solution:** Ensure all layout children are Dash components, strings, or numbers:
```python
# Wrong
html.Div([{'key': 'value'}])

# Right
html.Div([html.Span('value')])
```

### Components not rendering

**Possible causes:**
1. Missing `id` prop (required for callbacks)
2. JavaScript error - check browser console
3. Component library not installed or imported

**Debug:** Check browser DevTools console for errors.

## Import Errors

### "No module named 'dash_core_components'"

**Cause:** Using old import style.

**Solution:** Use new unified imports:
```python
# Old (deprecated)
import dash_core_components as dcc
import dash_html_components as html

# New
from dash import dcc, html
```

### "ImportError: cannot import name 'X' from 'dash'"

**Cause:** Feature not available in installed Dash version.

**Solution:** Upgrade Dash:
```bash
pip install --upgrade dash
```

## Server Errors

### "Address already in use"

**Cause:** Port 8050 (or specified port) is occupied.

**Solutions:**
1. Use different port: `app.run(port=8051)`
2. Kill existing process: `lsof -i :8050` then `kill <PID>`
3. Set via environment: `PORT=8051 python app.py`

### Hot reload not working

**Possible causes:**
1. `debug=False` (hot reload requires debug mode)
2. File outside watched directories
3. Syntax error preventing reload

**Solution:**
```python
app.run(
    debug=True,
    dev_tools_hot_reload=True,
    extra_hot_reload_paths=['./custom_modules/']
)
```

### "Working outside of application context"

**Cause:** Accessing Flask context outside request (e.g., in background thread).

**Solution:** Use `flask.current_app` inside callbacks, or pass data explicitly rather than using context.

## Background Callback Issues

### Background callback never completes

**Possible causes:**
1. Manager not configured correctly
2. Celery worker not running (for CeleryManager)
3. Exception in callback (check worker logs)

**Debug:** Check diskcache directory or Celery worker output for errors.

### "No such process" errors with DiskcacheManager

**Cause:** Process terminated unexpectedly.

**Solution:** Check for exceptions in the callback. Ensure `psutil` is installed.

### Progress updates not showing

**Cause:** `set_progress` not being called, or wrong output specified.

**Solution:** Ensure `progress` parameter matches an Output that exists:
```python
@app.callback(
    Output('result', 'children'),
    Input('btn', 'n_clicks'),
    progress=Output('progress', 'children'),  # Must exist in layout
    background=True,
    manager=manager,
)
def compute(set_progress, n):
    set_progress("Working...")  # Call this
    ...
```

## Async Callback Issues

### "You are trying to use a coroutine without dash[async]"

**Cause:** Using `async def` callback without async dependencies.

**Solution:**
```bash
pip install dash[async]
```

### Event loop errors in Jupyter

**Cause:** Conflicting event loops.

**Solution:** Dash automatically applies `nest_asyncio` in Jupyter. If issues persist:
```python
import nest_asyncio
nest_asyncio.apply()
```

## Multi-Page App Issues

### Pages not discovered

**Possible causes:**
1. Files don't contain `register_page(__name__)`
2. Files start with `_` or `.` (ignored)
3. Wrong `pages_folder` path

**Solution:** Ensure each page file has:
```python
from dash import register_page
register_page(__name__)

layout = ...
```

### "Page not found" for registered page

**Cause:** Path mismatch or routing issue.

**Debug:** Check `dash.page_registry` to see registered pages and their paths:
```python
from dash import page_registry
print(list(page_registry.values()))
```

## Component-Specific Issues

### Dropdown options not updating

**Cause:** Options list reference didn't change (same list object).

**Solution:** Return new list object:
```python
# Wrong - mutating existing list
options.append(new_option)
return options

# Right - return new list
return options + [new_option]
```

### Graph not updating

**Possible causes:**
1. Returning same figure object (reference equality)
2. Missing `figure` in Output

**Solution:** Create new figure object:
```python
return go.Figure(data=[...], layout={...})  # New object each time
```

### DataTable slow with large data

**Solutions:**
1. Enable virtualization: `virtualization=True`
2. Use pagination: `page_size=20, page_action='native'`
3. Filter data server-side before sending

## Testing Issues

### ChromeDriver version mismatch

**Error:** "session not created: This version of ChromeDriver only supports Chrome version X"

**Solution:** Update ChromeDriver to match your Chrome version:
```bash
# Check Chrome version
google-chrome --version

# Install matching chromedriver
pip install chromedriver-autoinstaller
```

### Tests hanging

**Possible causes:**
1. Callback never completing
2. Element selector not finding element
3. Timeout too short

**Solution:** Add explicit waits with longer timeout:
```python
dash_duo.wait_for_text_to_equal("#output", "expected", timeout=30)
```

### "Element not interactable"

**Cause:** Element hidden, overlapped, or not yet rendered.

**Solution:** Wait for element to be visible:
```python
dash_duo.wait_for_element("#button")
element = dash_duo.find_element("#button")
element.click()
```

## Build Issues

### "Component build failed"

**Possible causes:**
1. Node modules not installed: `npm ci`
2. Syntax error in React component
3. Missing dependencies

**Solution:** Check build output, ensure `npm ci` was run in component directory.

### "Module not found" after build

**Cause:** Python package not installed in editable mode.

**Solution:**
```bash
pip install -e .
```

## Performance Issues

### App slow to load

**Solutions:**
1. Use `eager_loading=False` (default) for lazy component loading
2. Minimize assets in `assets/` folder
3. Use `serve_locally=False` to serve from CDN

### Callbacks slow

**Solutions:**
1. Use `background=True` for expensive computations
2. Cache results with `@cache.memoize` or similar
3. Use clientside callbacks for simple transformations
4. Reduce data sent to/from server

### Memory growing over time

**Possible causes:**
1. Storing data in global variables
2. Background callback results not being cleaned up
3. Large figures being cached

**Solution:** Use `dcc.Store` for state, set `expire` on background managers, avoid global mutable state.
