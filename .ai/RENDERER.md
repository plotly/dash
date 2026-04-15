# Dash Renderer

The dash-renderer is the TypeScript/React frontend that powers Dash applications. Located in `dash/dash-renderer/src/`.

## Initialization Flow

```
1. DashRenderer constructor
   └─ ReactDOM.createRoot('#react-entry-point')
      └─ <AppProvider />

2. AppProvider creates Redux store
   └─ Registers observers for callback processing

3. APIController fetches from server
   ├─ GET /_dash-layout → component tree
   ├─ GET /_dash-dependencies → callback definitions
   └─ Dispatches setLayout, setGraphs, setPaths

4. Config includes children_props from ComponentRegistry
   └─ Stored in window.__dashprivate_childrenProps

5. hydrateInitialOutputs()
   ├─ Validates callbacks against layout
   ├─ Triggers initial callbacks
   └─ Sets appLifecycle: 'HYDRATED'

6. DashWrapper renders component tree
```

## Layout Traversal (crawlLayout)

The layout is traversed using `crawlLayout` (`actions/utils.js`). This algorithm:

1. **For arrays**: Iterates each child, following extra paths for nested components
2. **For objects (components)**:
   - Applies the visitor function to the component
   - Follows `props.children` if present
   - Follows additional paths from `children_props` config

### children_props

Each component class defines `_children_props` listing props that contain nested components. This is:
1. Generated from React component PropTypes/TypeScript during component generation
2. Stored on the Python component class as `_children_props`
3. Collected into `ComponentRegistry.children_props` when components are imported
4. Sent to frontend via config (`dash.py:933`)
5. Stored in `window.__dashprivate_childrenProps` on the frontend

```python
# Example: Python component class
class Dropdown(Component):
    _children_props = ['options.[].label', 'options.[].title']
    # ...
```

### Pattern Syntax

| Pattern | Meaning | Example |
|---------|---------|---------|
| `children` | Direct children prop | Standard |
| `prop.[]` | Array items are components | `options.[]` |
| `prop.[].sub` | `sub` prop of array items | `options.[].label` |
| `prop.{}` | Object values are components | Dynamic keys |
| `prop.{}.sub` | `sub` prop of object values | Nested dynamic |

### How crawlLayout Works

```javascript
crawlLayout(object, func, currentPath, extraPath)

// For each component:
// 1. Call func(object, currentPath)
// 2. If props.children exists, crawl it
// 3. For each path in children_props[namespace][type]:
//    - Parse the pattern (handle [], {})
//    - Crawl that path to find nested components
```

## Component Resolution

Components are resolved from `window[namespace][type]`:

```javascript
// Component packages register on window
window.dash_html_components = { Div, Span, H1, ... };
window.dash_core_components = { Dropdown, Graph, Input, ... };

// Registry.js resolves {type, namespace} → React component
Registry.resolve({type: 'Div', namespace: 'dash_html_components'})
// → window.dash_html_components.Div
```

## Callback Triggering

Callbacks are triggered by two sources:

### 1. Component setProps

When a component calls `setProps`, it triggers callbacks watching those props:

```javascript
// Component calls setProps
this.props.setProps({ value: newValue });

// DashWrapper.tsx handles this:
// 1. dispatch(updateProps(...))     → Updates layout in Redux
// 2. dispatch(notifyObservers(...)) → Finds and queues callbacks
```

`notifyObservers` calls `includeObservers` to find callbacks with matching inputs:

```javascript
// actions/index.js
export function notifyObservers({id, props}) {
  return async function (dispatch, getState) {
    const {graphs, paths} = getState();
    dispatch(
      addRequestedCallbacks(includeObservers(id, props, graphs, paths))
    );
  };
}
```

### 2. Callback Results

When a callback completes and updates component props, it also triggers dependent callbacks via `includeObservers` in the `executedCallbacks` observer.

## Callback Processing

Once callbacks are added to the queue, observers process them through states:

```
REQUESTED → PRIORITIZED → EXECUTING → EXECUTED → STORED
                              ↓
                          WATCHED (promises)
                              ↓
                          BLOCKED (waiting on deps)
```

### Observer Chain

1. **requestedCallbacks**: Deduplicates, checks dependencies, moves ready → prioritized
2. **prioritizedCallbacks**: Sorts by priority, executes (max 12 concurrent)
3. **executingCallbacks**: Tracks running callbacks, handles promises
4. **executedCallbacks**: Applies results to layout, triggers dependent callbacks
5. **isLoading**: Tracks loading state for `dcc.Loading`

## Redux Store

### Key Slices

```typescript
{
  layout: { ... },              // Component tree

  layoutHashes: {               // Change tracking for memoization
    "path": { hash, changedProps }
  },

  paths: {                      // ID → path mapping
    strs: { "my-id": [...path] },
    objs: { "type,index": [...] }  // Wildcards
  },

  callbacks: {                  // Pipeline states
    requested, prioritized, blocked,
    executing, watched, executed, stored
  },

  graphs: {                     // Dependency graph
    inputMap: { "id": { "prop": [callbacks] } }
  },

  config: {
    children_props: { ... },    // From ComponentRegistry
    // ...
  },

  isLoading: boolean
}
```

### Paths System

Maps component IDs to their location in layout:

```typescript
// String IDs
paths.strs["my-dropdown"] = ["layout", "props", "children", 2, "props"]

// Wildcard IDs (pattern-matching)
paths.objs["type,index"] = [
  { values: ["filter", 0], path: [...] },
  { values: ["filter", 1], path: [...] }
]
```

## window.dash_clientside

The clientside callback API (`utils/clientsideFunctions.ts`):

```javascript
window.dash_clientside = {
  no_update,        // Return to skip output
  PreventUpdate,    // Throw to cancel callback
  callback_context, // Current callback info
  set_props,        // Update props from clientside
  clean_url,        // URL sanitization
  Patch             // Partial prop updates
}
```

### callback_context

Available during callback execution:

```javascript
window.dash_clientside.callback_context = {
  triggered: [{ prop_id: "btn.n_clicks", value: 1 }],
  triggered_id: "btn",
  inputs: { "input.value": "hello" },
  states: { "store.data": {...} }
}
```

### Registering Clientside Functions

```javascript
// In assets/clientside.js
window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.my_namespace = {
  my_function: function(input_value) {
    return input_value.toUpperCase();
  }
};
```

### set_props

Update component props directly from clientside:

```javascript
// By string ID
window.dash_clientside.set_props('my-component', { value: 'new' });

// By pattern-matching ID
window.dash_clientside.set_props({ type: 'input', index: 0 }, { value: 'new' });
```

## window.dash_component_api

API for components to interact with Dash (`dashApi.ts`):

```javascript
window.dash_component_api = {
  ExternalWrapper,     // Render outside main tree
  DashContext,         // React Context
  useDashContext,      // Hook for context
  getLayout,           // Get props by ID/path
  stringifyId          // Convert wildcard IDs
}
```

### getLayout

Retrieve component props:

```javascript
const props = window.dash_component_api.getLayout('my-dropdown');
// → { id: 'my-dropdown', options: [...], value: 'a' }
```

### useDashContext

Hook for components:

```typescript
const {
  componentPath,
  isLoading,
  useSelector,
  useDispatch
} = useDashContext();
```

## Memoization

DashWrapper uses hash-based memoization. `layoutHashes` tracks which components changed:

```typescript
layoutHashes["0,props,children"] = {
  hash: 42,                      // Increments on change
  changedProps: { value: true }
}
```

Components only re-render when their hash changes.

## Key Files

| File | Purpose |
|------|---------|
| `DashRenderer.js` | Entry point |
| `AppProvider.react.tsx` | Redux store setup |
| `APIController.react.js` | Fetches layout, hydrates app |
| `wrapper/DashWrapper.tsx` | Component rendering, setProps |
| `actions/utils.js` | `crawlLayout` algorithm |
| `registry.js` | Component resolution |
| `reducers/layout.js` | Layout state |
| `reducers/callbacks.ts` | Callback pipeline |
| `reducers/config.js` | Stores children_props |
| `actions/index.js` | `notifyObservers` |
| `actions/dependencies_ts.ts` | `includeObservers`, callback matching |
| `observers/*.ts` | Callback processing |
| `utils/clientsideFunctions.ts` | Clientside API |
| `dashApi.ts` | Component API |
