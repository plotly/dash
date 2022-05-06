# How to make a new Dash back end

Dash as a framework purposely generally does as much of its work as it can in the front end, both as a way to maximize performance (limit the demand on servers, limit network latency) and as a way to make it easier to create new back ends. Nevertheless, the Python back end is generally the canonical implementation, both because it’s the first and because it lives in the same repo as the front end, https://github.com/plotly/dash

In order to make a new back end then, the primary goal is to replicate the functionality of the Python version. This doesn’t mean we need to match the Python syntax; each back end should implement features in a way that’s natural to users of that language, but all else equal keeping this syntax and naming close to the Python version will help with documentation and with cross-language usage, for example to allow Python users (who at least at first will outnumber users of other languages by a large margin) to help other users on the community forum.

## Dash Components

Fundamentally, Dash components are React components. Take a look at the contents of https://github.com/plotly/dash-core-components/tree/master/dash_core_components - in each component repo we generate assets that need to be served to the browser:
- one main JavaScript bundle (`dash_core_components.js`)
- maybe some sub-bundles to load asynchronously (`async-*.js`)
- normally a sourcemap for each bundle (`*.js.map`)

We also include a couple of files that are only used to generate the components:
- `metadata.json`: a structured description of each component and its react props and prop types
- `package-info.json`: a copy of the package.json file from the repo, mainly useful for grabbing the version number

Then we also have Python files. Most of these are generated directly from `metadata.json` - for example `Checklist.py` is a class definition corresponding to the Checklist React component, and if you look inside it you’ll see it inherits from the `dash.development.base_component.Component` class, it has a docstring listing all props and their types in Python notation (instead of “array of objects”, it says “list of dicts”), and it has a constructor that ensures you can only create it with appropriate props. Then there are some Python files that are NOT generated, but copied from https://github.com/plotly/dash-core-components/tree/master/dash_core_components_base - `__init__.py` collects all the component classes and explicitly lists all the browser assets in `_js_dist` and possibly `_css_dist`.

Each back end must have a way to generate its own wrappers for these React components. The Python wrappers are generated source code files as described above, created by [`_py_components_generation.py`](https://github.com/plotly/dash/blob/dev/dash/development/_py_components_generation.py) - other languages may choose to either generate files, or create precompiled objects of some sort, but the key requirements are:
- Provide a natural way for users of this language to create components as data structures, keeping in mind that components may be nested inside the children prop of some other components, and most props are optional.
- To the extent that we can help users with built-in documentation and IDE auto-completion, we should try to do that.
- When requested by the framework, the component must serialize to JSON. This looks like:
  `{"namespace": "dash_core_components", "type": "Checklist", "props": {...}}`
- When a component package is included in the program (ie, during the equivalent of the Python statement `import dash_core_components`) the package must make itself known to the framework, so that the framework knows to include the main JavaScript bundle in the HTML for the page and knows where to find all the other JS and related files. Notice how in `__init__.py` in `_js_dist` some files are marked `"async": True|"eager"|"lazy"` or `"dynamic": True`, but the main bundle `dash_core_components.js` has neither. This full complexity is not needed in a new back end, just know you can ignore `"async": "eager"` files and treat all of the others with flags as not to include in the initial HTML but to be served later if requested.
- Some packages also have CSS files that must be loaded for its components to look and function correctly. In Python we collect these in `_css_dist` and register them with Dash during package import, the same way we do with `_js_dist`.
- Note that we CANNOT wait until a component from the package has been instantiated to alert the framework that this package is in use. It’s very common for the initial page layout to not include components from all packages. This MUST happen earlier.
- The Python artifacts are generated in the same repo as the JavaScript source files. Currently this is also the case for R and Julia, but we’re moving away from that model. New back ends should copy these JavaScript bundles to a new repo, and generate whatever other artifacts they need in this new repo.

## Dash server routes

There is a relatively small set of routes (urls/url patterns) that a Dash server must be prepared to serve. A good way to get a feel for them is to load https://dash.plotly.com/ and look at the page structure (“Elements” tab in Chrome devtools) and the network requests that are made on page load and their responses (“Network” tab). You can see all of the route patterns if you look at the main [`dash.dash` file](https://github.com/plotly/dash/blob/dev/dash/dash.py) and search for `self._add_url` - plus the one `self.server.register_blueprint` call above it. These routes are:
- `""` and anything not caught by other routes listed below (see https://dash.plotly.com/urls): the “index” route, serving the HTML page skeleton. The Python back end implements a bunch of customization options for this, but for a first version these are unnecessary. See the template given in [`_default_index`](https://github.com/plotly/dash/blob/357f22167d40ef00c92ff165aa6df23c622799f6/dash/dash.py#L58-L74) for the basic structure and pieces that need to be included, most importantly `{%config}` that includes info like whether to display in-browser devtools, and `{%scripts}` and `{%renderer}` that load the necessary `<script>` tags and initialize the dash renderer.
- `_dash-component-suites/<package_name>/<path>`: serve the JavaScript and related files given by each component package, as described above. Note that we include an extra cache-busting portion in each filename. In the Python version this is the version number and unix timestamp of the file as reported by the filesystem
- `_dash-layout"`: Gives the JSON structure of the initial Dash components to render on the page (`app.layout` in Python)
- `_dash-dependencies`: A JSON array of all callback functions defined in the app.
- `_dash-update-component`: Handles all server-side callbacks. Responds in JSON. Note that `children` outputs can contain Dash components, which must be JSON encoded the same way as in `_dash-layout`.
- `_reload-hash`: once hot reloading is implemented and enabled (normally only during development), this route tells the page when something has changed on the server and the page should refresh.
- `_favicon.ico`: the favicon, the title bar icon for the page, normally the Plotly logo.
- `assets/<path>`: static files to use on the page, potentially nested. CSS and JS files in this directory should be included in the HTML index page, and any file in this directory should be served if requested by the page. In Python this is handled by the `register_blueprint` call.

## Choosing a web server

You'll need to choose an HTTP(S) server for the programming language that you're adding to the Dash framework. For example, here are the HTTP(S) servers currently uses for the existing known distributions of Dash:

- [Dash Python](https://github.com/plotly/dash) uses [Flask](https://github.com/pallets/flask/) (though there is also a [community-maintained version that uses Django](https://github.com/GibbsConsulting/django-plotly-dash))
- [Dash Julia](https://github.com/plotly/dash.jl) uses [HTTP.jl](https://github.com/JuliaWeb/HTTP.jl)
- [Dash.NET](https://github.com/plotly/dash.net) uses [Giraffe](https://github.com/giraffe-fsharp/Giraffe)
- [Dash.R](https://github.com/plotly/dashr) uses [Fiery](https://github.com/thomasp85/fiery)

## Dash App Objects

In Python, users first create a dash object:
```py
from dash import Dash
app = Dash(...)
```
Then they set the layout to some nested Dash components:
```py
app.layout = html.Div(...)
```
Then they add callbacks:
```py
@app.callback(Output(...), Input(...), Input(...), State(...), ...)
def my_callback(input1, input2, state):
    <do stuff>
    return my_output_value

app.clientside_callback(
    “<JavaScript function as a string or reference>”,
    Output(...), Input(...), Input(...), State(...), ...
)
```
And finally they run the server
```py
app.run_server(...)
```

Any new back end needs to provide all of that functionality, one way or another.

The `Dash()` constructor has lots of options. They’re all listed and documented [here]( https://github.com/plotly/dash/blob/357f22167d40ef00c92ff165aa6df23c622799f6/dash/dash.py#L113-L253) - some are Python-specific (`name`, `server`, `plugins`), others should eventually be replicated but many can be left out of the first proof-of-concept implementation.

Similarly the `app.run` (previously `app.run_server`) method has a lot of options, listed [here](https://github.com/plotly/dash/blob/357f22167d40ef00c92ff165aa6df23c622799f6/dash/dash.py#L1596-L1671) - again some are Python-specific (`flask_run_options`) and others can be added over time. Notice that many of these are simply passed on to `self.enable_dev_tools` - that’s because in Python the flask `server.run` command (called at the end of `app.run_server`) is normally only used in development, in production a more powerful server such as gunicorn is used, but a user may still want to enable devtools using a production server. You’re the expert on the new back end language, only you know if such a split makes sense. We don't want to write our own web server framework, you should be able to choose an existing one. Ideally this server should be easy to install on all major operating systems / platforms where your language is used, and for production scalability it should be able to run multiple workers or otherwise make full use of a multi-core machine. If it has the ability in development mode to create friendly error messages with stack traces to help debugging, that's a plus, but if not we can probably build that ourselves. 

## Contributing your own backends

We're very happy to work with anyone who is interested in making their own back end for Dash! Please get in touch through the [community forum](https://community.plotly.com/c/dash/) if you have started such an endeavor. In our experience, adding a new language to the Dash framework is not a weekend project, though we are constantly working to make this easier. At the moment, please anticipate a few months of work (including writing documentation). So far, mature Dash back ends exist for:

- [Python](https://github.com/plotly/dash)
- [Julia](https://github.com/plotly/dash.jl)
- [F#/.NET](https://github.com/plotly/dash.net)
- [R](https://github.com/plotly/dashr)

MATLAB, Scala, and SAS are examples of other scientific programming languages that could one day benefit from Dash's low-code, front end framework for creating AI and data science apps.

Happy coding!
