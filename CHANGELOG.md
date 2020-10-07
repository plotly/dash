# Change Log for Dash
All notable changes to `dash` will be documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/).

## [1.16.3] - 2020-10-07
### Fixed
- [#1426](https://github.com/plotly/dash/pull/1426) Fix a regression caused by `flask-compress==1.6.0` causing performance degradation on server requests

## [1.16.2] - 2020-09-25
### Fixed
- [#1415](https://github.com/plotly/dash/pull/1415) Fix a regression with some layouts callbacks involving dcc.Tabs, not yet loaded dash_table.DataTable and dcc.Graph to not be called
- [#1416](https://github.com/plotly/dash/pull/1416) Make callback graph more robust for complex apps and some specific props (`width` in particular) that previously caused errors.

## [1.16.1] - 2020-09-16
### Changed
- [#1376](https://github.com/plotly/dash/pull/1376) Extends the `getTransform` logic in the renderer to handle `persistenceTransforms` for both nested and non-nested persisted props. This was used to to fix [dcc#700](https://github.com/plotly/dash-core-components/issues/700) in conjunction with [dcc#854](https://github.com/plotly/dash-core-components/pull/854) by using persistenceTransforms to strip the time part of the datetime so that datepickers can persist when defined in callbacks.

### Fixed
- [#1408](https://github.com/plotly/dash/pull/1408) Fixes a bug where the callback graph layout would reset whenever a callback fired, losing user-initiated layout changes ([#1402](https://github.com/plotly/dash/issues/1402)) or creating a new force layout ([#1401](https://github.com/plotly/dash/issues/1401))

## [1.16.0] - 2020-09-03
### Added
- [#1371](https://github.com/plotly/dash/pull/1371) You can now get [CSP `script-src` hashes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/script-src) of all added inline scripts by calling `app.csp_hashes()` (both Dash internal inline scripts, and those added with `app.clientside_callback`) .

### Changed
- [#1385](https://github.com/plotly/dash/pull/1385) Closes [#1350](https://github.com/plotly/dash/issues/1350) and fixes a previously undefined callback behavior when multiple elements are stacked on top of one another and their `n_clicks` props are used as inputs of the same callback. The callback will now trigger once with all the triggered `n_clicks` props changes.
- [#1179](https://github.com/plotly/dash/pull/1179) New and improved callback graph in the debug menu. Now based on Cytoscape for much more interactivity, plus callback profiling including number of calls, fine-grained time information, bytes sent and received, and more. You can even add custom timing information on the server with `callback_context.record_timing(name, seconds)`

### Fixed
- [#1384](https://github.com/plotly/dash/pull/1384) Fixed a bug introduced by [#1180](https://github.com/plotly/dash/pull/1180) breaking use of `prevent_initial_call` as a positional arg in callback definitions

## [1.15.0] - 2020-08-25
### Added
- [#1355](https://github.com/plotly/dash/pull/1355) Removed redundant log message and consolidated logger initialization. You can now control the log level - for example suppress informational messages from Dash with `app.logger.setLevel(logging.WARNING)`.
- [#1253](https://github.com/plotly/dash/pull/1253), [#1377](https://github.com/plotly/dash/pull/1377) Added experimental `--jl-prefix` option to `dash-generate-components`, optionally generates Julia version of components and corresponding Julia package

### Changed
- [#1180](https://github.com/plotly/dash/pull/1180) and [#1375](https://github.com/plotly/dash/pull/1375) `Input`, `Output`, and `State` in callback definitions don't need to be in lists. You still need to provide `Output` items first, then `Input` items, then `State`, and the list form is still supported. In particular, if you want to return a single output item wrapped in a length-1 list, you should still wrap the `Output` in a list. This can be useful for procedurally-generated callbacks.
- [#1368](https://github.com/plotly/dash/pull/1368) Updated pytest to v6.0.1. To avoid deprecation warnings, this also updated pytest-sugar to 0.9.4 and pytest-mock to 3.2.0. The pytest-mock update only effects python >= 3.0. Pytest-mock remains pinned at 2.0.0 for python == 2.7.

## [1.14.0] - 2020-07-27
### Added
- [#1343](https://github.com/plotly/dash/pull/1343) Add `title` parameter to set the
document title. This is the recommended alternative to setting app.title or overriding
the index HTML.
- [#1315](https://github.com/plotly/dash/pull/1315) Add `update_title` parameter to set or disable the "Updating...." document title during updates. Closes [#856](https://github.com/plotly/dash/issues/856) and [#732](https://github.com/plotly/dash/issues/732)

## [1.13.4] - 2020-06-25
### Fixed
- [#1310](https://github.com/plotly/dash/pull/1310) Fix a regression since 1.13.0 preventing more than one loading state from being shown at a time.

## [1.13.3] - 2020-06-19

## [1.13.2] - 2020-06-18
### Fixed
- [#1305](https://github.com/plotly/dash/issues/1305)
    - Fix regression that causes crash when `FLASK_ENV` is modified during app execution
    - Fix regression that caused tests using `_wait_for_callbacks` to fail

## [1.13.1] - 2020-06-17

## [1.13.0] - 2020-06-17
### Added
- [#1289](https://github.com/plotly/dash/pull/1289) Supports `DASH_PROXY` env var to tell `app.run_server` to report the correct URL to view your app, when it's being proxied. Throws an error if the proxy is incompatible with the host and port you've given the server.
- [#1240](https://github.com/plotly/dash/pull/1240) Adds `callback_context` to clientside callbacks (e.g. `dash_clientside.callback_context.triggered`). Supports `triggered`, `inputs`, `inputs_list`, `states`, and `states_list`, all of which closely resemble their serverside cousins.

### Changed
- [#1237](https://github.com/plotly/dash/pull/1237) Closes [#920](https://github.com/plotly/dash/issues/920): Converts hot reload fetch failures into a server status indicator showing whether the latest fetch succeeded or failed. Callback fetch failures still appear as errors but have a clearer message.
- [#1254](https://github.com/plotly/dash/pull/1254) Modifies the callback chain implementation and improves performance for apps with a lot of components

### Fixed
- [#1255](https://github.com/plotly/dash/pull/1255) Hard hot reload targets only the current window, not the top - so if your app is in an iframe you will only reload the app
- [#1249](https://github.com/plotly/dash/pull/1249) Fixes [#919](https://github.com/plotly/dash/issues/919) so `dash.testing` is compatible with more `pytest` plugins, particularly `pytest-flake8` and `pytest-black`.
- [#1248](https://github.com/plotly/dash/pull/1248) Fixes [#1245](https://github.com/plotly/dash/issues/1245), so you can use prop persistence with components that have dict IDs, ie for pattern-matching callbacks.
- [#1185](https://github.com/plotly/dash/pull/1185) Sort asset directories, same as we sort files inside those directories. This way if you need your assets loaded in a certain order, you can add prefixes to subdirectory names and enforce that order.
- [#1288](https://github.com/plotly/dash/pull/1288) Closes [#1285](https://github.com/plotly/dash/issues/1285): Debug=True should work in the __main__ module.

## [1.12.0] - 2020-05-05
### Added
- [#1228](https://github.com/plotly/dash/pull/1228) Adds control over firing callbacks on page (or layout chunk) load. Individual callbacks can have their initial calls disabled in their definition `@app.callback(..., prevent_initial_call=True)` and similar for `app.clientside_callback`. The app-wide default can also be changed with `app=Dash(prevent_initial_callbacks=True)`, then individual callbacks may disable this behavior.
- [#1201](https://github.com/plotly/dash/pull/1201) New attribute `app.validation_layout` allows you to create a multi-page app without `suppress_callback_exceptions=True` or layout function tricks. Set this to a component layout containing the superset of all IDs on all pages in your app.
- [#1078](https://github.com/plotly/dash/pull/1078) Permit usage of arbitrary file extensions for assets within component libraries

### Fixed
- [#1224](https://github.com/plotly/dash/pull/1224) Fixes [#1223](https://github.com/plotly/dash/issues/1223), a very specific situation in which initial callbacks will not fire.
- [#1220](https://github.com/plotly/dash/pull/1220) Fixes [#1216](https://github.com/plotly/dash/issues/1216), a set of related issues about pattern-matching callbacks with `ALL` wildcards in their `Output` which would fail if no components matched the pattern.
- [#1212](https://github.com/plotly/dash/pull/1212) Fixes [#1200](https://github.com/plotly/dash/issues/1200) - prior to Dash 1.11, if none of the inputs to a callback were on the page, it was not an error. This was, and is now again, treated as though the callback raised PreventUpdate. The one exception to this is with pattern-matching callbacks, when every Input uses a multi-value wildcard (ALL or ALLSMALLER), and every Output is on the page. In that case the callback fires as usual.
- [#1201](https://github.com/plotly/dash/pull/1201) Fixes [#1193](https://github.com/plotly/dash/issues/1193) - prior to Dash 1.11, you could use `flask.has_request_context() == False` inside an `app.layout` function to provide a special layout containing all IDs for validation purposes in a multi-page app. Dash 1.11 broke this when we moved most of this validation into the renderer. This change makes it work again.

## [1.11.0] - 2020-04-10
### Added
- [#1103](https://github.com/plotly/dash/pull/1103) Pattern-matching IDs and callbacks. Component IDs can be dictionaries, and callbacks can reference patterns of components, using three different wildcards: `ALL`, `MATCH`, and `ALLSMALLER`, available from `dash.dependencies`. This lets you create components on demand, and have callbacks respond to any and all of them. To help with this, `dash.callback_context` gets three new entries: `outputs_list`, `inputs_list`, and `states_list`, which contain all the ids, properties, and except for the outputs, the property values from all matched components.
- [#1103](https://github.com/plotly/dash/pull/1103) `dash.testing` option `--pause`: after opening the dash app in a test, will invoke `pdb` for live debugging of both Javascript and Python. Use with a single test case like `pytest -k cbwc001 --pause`.

### Changed
- [#1103](https://github.com/plotly/dash/pull/1103) Multiple changes to the callback pipeline:
  - `dash.callback_context.triggered` now does NOT reflect any initial values, and DOES reflect EVERY value which has been changed either by activity in the app or as a result of a previous callback. That means that the initial call of a callback with no prerequisite callbacks will list nothing as triggering. For backward compatibility, we continue to provide a length-1 list for `triggered`, but its `id` and `property` are blank strings, and `bool(triggered)` is `False`.
  - A user interaction which returns the same property value as was previously present will not trigger the component to re-render, nor trigger callbacks using that property as an input.
  - Callback validation is now mostly done in the browser, rather than in Python. A few things - mostly type validation, like ensuring IDs are strings or dicts and properties are strings - are still done in Python, but most others, like ensuring outputs are unique, inputs and outputs don't overlap, and (if desired) that IDs are present in the layout, are done in the browser. This means you can define callbacks BEFORE the layout and still validate IDs to the layout; and while developing an app, most errors in callback definitions will not halt the app.

### Fixed
- [#1103](https://github.com/plotly/dash/pull/1103) Fixed multiple bugs with chained callbacks either not triggering, inconsistently triggering, or triggering multiple times. This includes: [#635](https://github.com/plotly/dash/issues/635), [#832](https://github.com/plotly/dash/issues/832), [#1053](https://github.com/plotly/dash/issues/1053), [#1071](https://github.com/plotly/dash/issues/1071), and [#1084](https://github.com/plotly/dash/issues/1084). Also fixed [#1105](https://github.com/plotly/dash/issues/1105): async components that aren't rendered by the page (for example in a background Tab) would block the app from executing callbacks.

## [1.10.0] - 2020-04-01
### Added
- [#1134](https://github.com/plotly/dash/pull/1134) Allow `dash.run_server()` host and port parameters to be set with environment variables HOST & PORT, respectively

### Changed
- [#1145](https://github.com/plotly/dash/pull/1145) Update from React 16.8.6 to 16.13.0

### Fixed
- [#1142](https://github.com/plotly/dash/pull/1142) [Persistence](https://dash.plot.ly/persistence): Also persist 0, empty string etc

## [1.9.1] - 2020-02-27
### Added
- [#1133](https://github.com/plotly/dash/pull/1133) Allow the `compress` config variable to be set with an environment variable with DASH_COMPRESS=FALSE

## [1.9.0] - 2020-02-04
### Fixed
- [#1080](https://github.com/plotly/dash/pull/1080) Handle case where dash fails to load when used inside an iframe with a sandbox attribute that only has allow-scripts

## [1.8.0] - 2020-01-14
### Added
- [#1073](https://github.com/plotly/dash/pull/1073) Two new functions to simplify usage handling URLs and pathnames: `app.get_relative_path` & `app.trim_relative_path`.
These functions are particularly useful for apps deployed on Dash Enterprise where the apps served under a URL prefix (the app name) which is unlike apps served on localhost:8050.
    - `app.get_relative_path` returns a path with the config setting `requests_pathname_prefix` prefixed. Use `app.get_relative_path` anywhere you would provide a relative pathname, like `dcc.Link(href=app.relative_path('/page-2'))` or even as an alternative to `app.get_asset_url` with e.g. `html.Img(src=app.get_relative_path('/assets/logo.png'))`.
    - `app.trim_relative_path` a path with `requests_pathname_prefix` and leading & trailing
    slashes stripped from it. Use this function in callbacks that deal with `dcc.Location` `pathname`
    routing.
    Example usage:
    ```python
    app.layout = html.Div([
        dcc.Location(id='url'),
        html.Div(id='content')
    ])
    @app.callback(Output('content', 'children'), [Input('url', 'pathname')])
    def display_content(path):
        page_name = app.strip_relative_path(path)
        if not page_name:  # None or ''
            return html.Div([
                html.Img(src=app.get_relative_path('/assets/logo.png')),
                dcc.Link(href=app.get_relative_path('/page-1')),
                dcc.Link(href=app.get_relative_path('/page-2')),
            ])
        elif page_name == 'page-1':
            return chapters.page_1
        if page_name == "page-2":
            return chapters.page_2
    ```

### Changed
- [#1035](https://github.com/plotly/dash/pull/1035) Simplify our build process.
- [#1074](https://github.com/plotly/dash/pull/1074) Error messages when providing an incorrect property to a component have been improved: they now specify the component type, library, version, and ID (if available).

### Fixed
- [#1037](https://github.com/plotly/dash/pull/1037) Fix no_update test to allow copies, such as those stored and retrieved from a cache.

## [1.7.0] - 2019-11-27
### Added
- [#967](https://github.com/plotly/dash/pull/967) Add support for defining
clientside JavaScript callbacks via inline strings.
- [#1020](https://github.com/plotly/dash/pull/1020) Allow `visit_and_snapshot` API in `dash.testing.browser` to stay on the page so you can run other checks.

### Changed
- [#1026](https://github.com/plotly/dash/pull/1026) Better error message when you forget to wrap multiple `children` in an array, and they get passed to other props.

### Fixed
- [#1018](https://github.com/plotly/dash/pull/1006) Fix the `dash.testing` **stop** API with process application runner in Python2. Use `kill()` instead of `communicate()` to avoid hanging.
- [#1027](https://github.com/plotly/dash/pull/1027) Fix bug with renderer callback lock never resolving with non-rendered async component using the asyncDecorator

## [1.6.1] - 2019-11-14
### Fixed
- [#1006](https://github.com/plotly/dash/pull/1006) Fix IE11 / ES5 compatibility and validation issues
- [#1006](https://github.com/plotly/dash/pull/1006) Fix bug with renderer wrapper component TreeContainer to prevent useless re-renders
- [#1001](https://github.com/plotly/dash/pull/1001)
  - Fix and improve the `clear_input()` API in `dash.testing`, so it's more robust handling react `input`.
  - make the `percy_snapshot()` API more robust, and the timeout of `wait_for_callbacks` (if set to True) will not fail the snapshot execution, but logged as potential error.

## [1.6.0] - 2019-11-04
### Fixed
- [#999](https://github.com/plotly/dash/pull/999) Fix fingerprint for component suites with `metadata` in version.
- [#983](https://github.com/plotly/dash/pull/983) Fix the assets loading issues when dashR application runner is handling with an app defined by string chunk.

## [1.5.1] - 2019-10-29
### Fixed
- [#987](https://github.com/plotly/dash/pull/987) Fix cache string handling for component suites with nested folders in their packages.
- [#986](https://github.com/plotly/dash/pull/986) Fix a bug with evaluation of `_force_eager_loading` when application is loaded with gunicorn

## [1.5.0] - 2019-10-29
### Added
- [#964](https://github.com/plotly/dash/pull/964) Adds support for preventing updates in clientside functions.
  - Reject all updates with `throw window.dash_clientside.PreventUpdate;`
  - Reject a single output by returning `window.dash_clientside.no_update`
- [#899](https://github.com/plotly/dash/pull/899) Add support for async dependencies and components
- [#973](https://github.com/plotly/dash/pull/973) Adds support for resource caching and adds a fallback caching mechanism through etag

### Fixed
- [#974](https://github.com/plotly/dash/pull/974) Fix and improve a percy snapshot behavior issue we found in dash-docs testing. It adds a flag `wait_for_callbacks` to ensure that, in the context of a dash app testing, the percy snapshot action will happen only after all callbacks get fired.

## [1.4.1] - 2019-10-17
### Fixed
- [#969](https://github.com/plotly/dash/pull/969) Fix warnings emitted by react devtools coming from our own devtools components.

## [1.4.0] - 2019-10-08
### Added
- [#948](https://github.com/plotly/dash/pull/948) Support setting working directory for R apps run using the `dashr` fixture, primarily useful for tests with assets. `dashr.start_server` supports a `cwd` argument to set an explicit working directory, and has smarter defaults when it's omitted: if `app` is a path to an R script, uses the directory of that path; if `app` is a string, uses the directory the test file itself is in.
- [#944](https://github.com/plotly/dash/pull/944)
  - Relevant `dash.testing` methods can now be called with either an element or a CSS selector: `select_dcc_dropdown`, `multiple_click`, `clear_input`, `zoom_in_graph_by_ratio`, `click_at_coord_fractions`.
  - Three new `dash.testing` methods: `clear_local_storage`, `clear_session_storage`, and `clear_storage` (to clear both together)
- [#937](https://github.com/plotly/dash/pull/937) `dash.testing` adds two APIs `zoom_in_graph_by_ratio` and `click_at_coord_fractions` about advanced interactions using mouse `ActionChain`
- [#938](https://github.com/plotly/dash/issues/938) Add debugging traces to dash backend about serving component suites, to verify the installed packages whenever in doubt.

### Fixed
- [#944](https://github.com/plotly/dash/pull/944) Fix a bug with persistence being toggled on/off on an existing component.

## [1.3.1] - 2019-09-19
### Changed
- Bump dash-core-components version from 1.2.0 to [1.2.1](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#120---2019-09-19)

## [1.3.0] - 2019-09-17
### Added
- [#923](https://github.com/plotly/dash/pull/923) Add one configuration `--percy-assets` in `pytest` to specify extra application assets path if needed.

- [#918](https://github.com/plotly/dash/pull/918) Add `wait_for_element_by_id` and `visit_and_snapshot` APIs in browser, add `raw_command` option (with higher priority than the default waitress one) and optional `start_timeout` argument to handle large applications within the process runner.

- [#903](https://github.com/plotly/dash/pull/903) Persistence: enable props edited by the user to persist across recreating the component or reloading the page. Components need to define three new props: `persistence`, `persisted_props`, and `persistence_type` as described in the lead comment of `src/persistence.js`. App developers then enable this behavior by, in the simplest case, setting `persistence: true` on the component. First use case is table, see [dash-table#566](https://github.com/plotly/dash-table/pull/566)

### Changed
- Bump dash-table version from 4.2.0 to [4.3.0](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#430---2019-09-17)
- Bump dash-core-components version from 1.1.2 to [1.2.0](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#120---2019-09-17)
- Bump dash-renderer version from 1.0.1 to [1.1.0](https://github.com/plotly/dash/blob/master/dash-renderer/CHANGELOG.md#110---2019-09-17)

### Fixed
- [#915](https://github.com/plotly/dash/issues/915) Fix `dash-generate-components` on Windows.
- [#829](https://github.com/plotly/dash/issues/829) Fix the `--remote` pytest argument which was not effective in the code, adding a new argument `--remote-url` to support the selenium grid usage in the cloud.
- [#910](https://github.com/plotly/dash/pull/910) Reduce the dash-renderer packages size on **PyPI** about 55% by removing the source maps. To do more advanced debugging, the source maps needs to be generated from source code with `npm run build:local` and pip install in editable mode, i.e. `pip install -e .`

## [1.2.0] - 2019-08-27
### Added
- [#860](https://github.com/plotly/dash/pull/860) Add a new arg `dev_tools_prune_errors` to `app.run_server` and `app.enable_dev_tools`. Default `True`, tracebacks only include user code and below. Set it `False` for the previous behavior showing all the Dash and Flask parts of the stack.

### Changed
- Bump dash-table version from 4.1.0 to [4.2.0](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#420---2019-08-27)
- Bump dash-core-components version from 1.1.1 to [1.1.2](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#112---2019-08-27)
- Bump dash-html-components version from 1.0.0 to [1.0.1](https://github.com/plotly/dash-html-components/blob/master/CHANGELOG.md#101---2019-08-27)
- Bump dash-renderer version from 1.0.0 to [1.0.1](https://github.com/plotly/dash/blob/dev/dash-renderer/CHANGELOG.md#101---2019-08-27)

### Fixed
- [#874](https://github.com/plotly/dash/pull/874) Clean all the binary assets in dash-renderer, add tool to build all the required bundles from fresh source code to avoid confusion of the assets and improve the release process. Fixes [#868](https://github.com/plotly/dash/pull/868) and [#734](https://github.com/plotly/dash/pull/734)

## [1.1.1] - 2019-08-06
### Changed
- Bump dash-core-components version from 1.1.0 to [1.1.1](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#111---2019-08-06)

## [1.1.0] - 2019-08-05
### Added
- [#827](https://github.com/plotly/dash/pull/827) Add support for dashR testing to the `dash.testing` pytest framework.

### Changed
- Bump dash-table version from 4.0.2 to [4.1.0](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#410---2019-08-05)
- Bump dash-core-components version from 1.0.0 to [1.1.0](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#110---2019-08-05)

## [1.0.2] - 2019-07-15
### Changed
- Bump dash-table version from 4.0.1 to [4.0.2](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#402---2019-07-15)

### Fixed
- [#821](https://github.com/plotly/dash/pull/821) Fix a bug with callback error reporting, [#791](https://github.com/plotly/dash/issues/791).

## [1.0.1] - 2019-07-09
### Changed
- 💥 [#808](https://github.com/plotly/dash/pull/808) Remove strong `dash.testing` dependencies per community feedback. Testing users should do `pip install dash[testing]` afterwards.

- [#805](https://github.com/plotly/dash/pull/805) Add headless mode for dash.testing, add `pytest_setup_options` hook for full configuration of `WebDriver Options`.

- Bump dash-table version from 4.0.0 to [4.0.1](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#401---2019-07-09)

## [1.0.0] - 2019-06-20
### Changed
- 💥 [#761](https://github.com/plotly/dash/pull/761) Several breaking changes to the `dash.Dash` API:
  - Remove two obsolete constructor kwargs: `static_folder` and `components_cache_max_age`
  - Remove the misspelled `supress_callback_exceptions` fallback
  - Remove the unused `resources.config.infer_from_layout`
  - Revamp `app.config`: ALL constructor args are now stored in `config`, with three exceptions: `server`, `index_string`, and `plugins`. None of these are stored in any other instance attributes anymore.
  - Change `hot_reload_interval` from msec to seconds, for consistency with `hot_reload_watch_interval`
  - When called from `enable_dev_tools`, `debug=True` by default. It's still `False` by default from `run_server`.

- ✨ [#744](https://github.com/plotly/dash/pull/744) Introducing Dash Testing (`dash.testing`) - read the full tutorial at <https://dash.plotly.com/testing>.

- [#753](https://github.com/plotly/dash/pull/753) `Component` no longer inherits `MutableMapping`, so `values`, `keys`, and more are no longer methods. Fixes an issue reported in [dcc#440](https://github.com/plotly/dash-core-components/issues/440) where components with certain prop names defined but not provided would cause a failure to render. During component generation we now disallow all props with leading underscores or matching a few remaining reserved words: `UNDEFINED`, `REQUIRED`, `to_plotly_json`, `available_properties`, and `available_wildcard_properties`.

- [#739](https://github.com/plotly/dash/pull/739) Allow the Flask app to be provided to Dash after object initialization. This allows users to define Dash layouts etc when using the app factory pattern, or any other pattern that inhibits access to the app object. This broadly complies with the flask extension API, allowing Dash to be considered as a Flask extension where it needs to be.

- [#774](https://github.com/plotly/dash/pull/774) Allow the Flask app to set the Dash app name if the name is not provided by users.

- [#722](https://github.com/plotly/dash/pull/722) Assets are served locally by default. Both JS scripts and CSS files are affected. This improves robustness and flexibility in numerous situations, but in certain cases initial loading could be slowed. To restore the previous CDN serving, set `app.scripts.config.serve_locally = False` (and similarly with `app.css`, but this is generally less important).

- [#724](https://github.com/plotly/dash/pull/724), [renderer#175](https://github.com/plotly/dash-renderer/pull/175) Undo/redo toolbar is removed by default, you can enable it with `app=Dash(show_undo_redo=true)`. The CSS hack `._dash-undo-redo:{display:none;}` is no longer needed

- 💥[#709](https://github.com/plotly/dash/pull/709) Merge the `dash-renderer` project into the main dash repo to simplify feature dev workflow. We will keep the [deprecated one](https://github.com/plotly/dash-renderer) for archive purpose.

## [0.43.0] - 2019-05-15
### Changed
- Bump dash-core-components version from 0.47.0 to [0.48.0](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#0480---2019-05-15)
- Bump dash-renderer version from 0.23.0 to [0.24.0](https://github.com/plotly/dash-renderer/blob/master/CHANGELOG.md#0240---2019-05-15)
- Bump dash-table version from 3.6.0 to [3.7.0](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#370---2019-05-15)

### Fixed
- [renderer#170](https://github.com/plotly/dash-renderer/pull/170) Fix regression on handling PreventUpdate (204 NO CONTENT)

## [0.42.0] - 2019-04-25
### Added
- [#687](https://github.com/plotly/dash/pull/687), [renderer#100](https://github.com/plotly/dash-renderer/pull/100) Dev Tools support. A new UI in the application that automatically display JavaScript & Python error messages, validates your component's properties, and displays a graph of your callback's dependencies. Only enabled in debug mode. Turn this on and off with two new config flags in `app.run_server`:
  - `dev_tools_props_check` - turn on/off property validation.
  - `dev_tools_ui` - turn on/off the UI.

### Fixed
- [renderer#148](https://github.com/plotly/dash-renderer/issues/148) Fix regression for `children=0` case.

## [0.41.0] - 2019-04-10
### Added
- [#672](https://github.com/plotly/dash/pull/672), [renderer#143](https://github.com/plotly/dash-renderer/pull/143) Support for "Clientside Callbacks" - an escape hatch to execute your callbacks in JavaScript instead of Python
- [#676](https://github.com/plotly/dash/pull/676) Add `dev_tools_ui` config flag in `app.run_server` (serialized in `<script id="_dash-config" type="application/json">`) to display or hide the forthcoming Dev Tools UI in Dash's front-end (dash-renderer).
- [#680](https://github.com/plotly/dash/pull/680) Partial updates: leave some multi-output updates unchanged while updating others

### Removed
- [renderer#145](https://github.com/plotly/dash-renderer/pull/145) Remove `dash_renderer._set_react_version` support for 15.4.2 and 16.2.0

### Changed
- Bump dash-core-components version from 0.45.0 to [0.46.0](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#0460---2019-04-10)
- [renderer#145](https://github.com/plotly/dash-renderer/pull/145) Update from React 15.4.2 to React 16.8.6

## [0.40.0] - 2019-03-25
### Changed
- Bump dash-core-components version from 0.44.0 to [0.45.0](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#0450---2019-03-25)
- Bump dash-html-components version from 0.14.0 to [0.15.0](https://github.com/plotly/dash-html-components/blob/master/CHANGELOG.md#0150---2019-03-25)
- [renderer#140](https://github.com/plotly/dash-renderer/pull/140), [renderer#126](https://github.com/plotly/dash-renderer/pull/126) Optimize rendering, and always assign `setProps` to components even with no callbacks to use it.

## [0.39.0] - 2019-03-04
### Added
- [#436](https://github.com/plotly/dash/pull/436) Allow multiple outputs from a single callback.
- [#367](https://github.com/plotly/dash/pull/367) Support custom JavaScript hooks to modify callback payloads and responses.
- [#623](https://github.com/plotly/dash/pull/623) Modify the flask response with custom cookies or headers, using `dash.callback_context.response`.
- [renderer#93](https://github.com/plotly/dash-renderer/pull/93) Loading states API

### Changed
- Bump dash-core-components version from 0.43.1 to [0.44.0](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#0440---2019-03-04)
- Bump dash-html-components version from 0.13.5 to [0.14.0](https://github.com/plotly/dash-html-components/blob/master/CHANGELOG.md#0140---2019-03-04)
- Bump dash-table version from 3.5.0 to [3.6.0](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#360---2019-03-04)

## [0.38.0] - 2019-02-25
### Added
- [#603](https://github.com/plotly/dash/pull/603) Add components libraries js/css distribution to hot reload watch.
- [#608](https://github.com/plotly/dash/pull/608), [renderer#124](https://github.com/plotly/dash-renderer/pull/124) Callback context:
  - Know which inputs caused a callback to fire: `dash.callback_context.triggered`
  - Input/State values by name `dash.callback_context.states.get('btn.n_clicks')`

### Changed
- Bump dash-table version from 3.4.0 to [3.5.0](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#350---2019-02-25)
- Bump dash-renderer version from 0.18.0 to [0.19.0](https://github.com/plotly/dash-renderer/blob/master/CHANGELOG.md#0190---2019-02-25)

### Fixed
- Fix missing indentation for generated metadata.json [#600](https://github.com/plotly/dash/issues/600)
- Fix missing component prop docstring error [#598](https://github.com/plotly/dash/issues/598)
- [#492](https://github.com/plotly/dash/pull/492) Move `__repr__` to base component instead of being generated.
- [#605](https://github.com/plotly/dash/pull/605) Raise exception when same input & output are used in a callback

## [0.37.0] - 2019-02-11
### Removed
- [renderer#118](https://github.com/plotly/dash-renderer/pull/118) Removed redux logger for the dev.

### Changed
- [#565](https://github.com/plotly/dash/pull/565) Add core libraries as version locked dependencies
- Bump dash-table version from 3.3.0 to [3.4.0](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#340---2019-02-08)
- Bump dash-renderer version from 0.17.0 to [0.18.0](https://github.com/plotly/dash-renderer/blob/master/CHANGELOG.md#0180---2019-02-11)
- Bump dash-core-components version from 0.43.0 to [0.43.1](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#0431---2019-02-11)

### Fixed
- [#563](https://github.com/plotly/dash/pull/563) Fix collections.abc deprecation warning for Python 3.8

## [0.36.0] - 2019-01-25
### Removed
- [#550](https://github.com/plotly/dash/pull/550), [renderer#114](https://github.com/plotly/dash-renderer/pull/114) Remove support for `Event` system. Use event properties instead, for example the `n_clicks` property instead of the `click` event, see [#531](https://github.com/plotly/dash/issues/531). `dash_renderer` MUST be upgraded to >=0.17.0 together with this, and it is recommended to update `dash_core_components` to >=0.43.0 and `dash_html_components` to >=0.14.0.

## [0.35.3] - 2019-01-23
### Changed
- [#547](https://github.com/plotly/dash/pull/547)
  - `assets_folder` argument now defaults to 'assets'
  - The assets folder is now always relative to the given root path of `name` argument, the default of `__main__` will get the `cwd`.
  - No longer coerce the name argument from the server if the server argument is provided.

### Fixed
- [#547](https://github.com/plotly/dash/pull/547)
  - Asset blueprint takes routes prefix into it's static path.
  - Asset url path no longer strip routes from requests.
- [#548](https://github.com/plotly/dash/pull/548) Remove print statement from PreventUpdate error handler.
- [#524](https://github.com/plotly/dash/pull/524) Removed ComponentRegistry dist cache.

## [0.35.2] - 2019-01-11
### Fixed
- [#522](https://github.com/plotly/dash/pull/522) Fix typo in some exception names
- [renderer#110](https://github.com/plotly/dash-renderer/pull/110)
  - Keep the config store state on soft reload.
  - AppProvider returns `Loading...` if no configs as before [renderer#108](https://github.com/plotly/dash-renderer/pull/108).

## 0.35.1 - 2018-12-27
### Fixed
- [#518](https://github.com/plotly/dash/pull/518) Always skip `dynamic` resources from index resources collection.

## 0.35.0 - 2018-12-18
### Added
- [#483](https://github.com/plotly/dash/pull/483) Experimental `--r-prefix` option to `dash-generate-components`, optionally generates R version of components and corresponding R package.

## 0.34.0 - 2018-12-17
### Added
- [#490](https://github.com/plotly/dash/pull/490) Add `--ignore` option to `dash-generate-components`, defaults to `^_`.

### Removed
- [renderer#108](https://github.com/plotly/dash-renderer/pull/108) Unused login api and Authentication component

### Fixed
- Add `key` to rendered components, fixing [renderer#379](https://github.com/plotly/dash-core-components/issues/379)

## 0.33.0 - 2018-12-10
### Added
- [#487](https://github.com/plotly/dash/pull/487) Add specific Dash exception types to replace generic exceptions (`InvalidIndexException`, `DependencyException`, `ResourceException`)

## 0.32.2 - 2018-12-09
### Fixed
- [#485](https://github.com/plotly/dash/pull/485) Fix typo in missing events/inputs error message

## 0.32.1 - 2018-12-07
### Changed
- [#484](https://github.com/plotly/dash/pull/484) Mute dash related missing props docstring from extract-meta warnings

## 0.32.0 - 2018-12-07
### Added
- [#478](https://github.com/plotly/dash/pull/478), [renderer#104](https://github.com/plotly/dash-renderer/issues/104) Support for .map file extension and dynamic (on demand) loading
- [renderer#107](https://github.com/plotly/dash-renderer/pull/107) [Redux devtools](https://github.com/zalmoxisus/redux-devtools-extension) support

## 0.31.1 - 2018-11-29
### Fixed
- [#473](https://github.com/plotly/dash/pull/473) Fix `_imports_.py` indentation generation.

## 0.31.0 - 2018-11-29
### Added
- [#451](https://github.com/plotly/dash/pull/451) Combine `extract-meta` and Python component files generation in a cli

### Fixed
- Fix a bug [renderer#66](https://github.com/plotly/dash-renderer/issues/66) in the ON_PROP_CHANGE callback where history was not correctly set when acting on more than one component. In particular, the 'undo' button should now work as expected.

## 0.30.0 - 2018-11-14
### Added
- [#362](https://github.com/plotly/dash/pull/362), [renderer#73](https://github.com/plotly/dash-renderer/pull/73) Hot reloading from the browser.
- Silence routes logging with `dev_tools_silence_routes_logging`.

## 0.29.0 - 2018-11-06
### Added
- [#444](https://github.com/plotly/dash/pull/444) Add component namespaces registry, collect the resources needed by component library when they are imported instead of crawling the layout.

## 0.28.7 - 2018-11-05
### Fixed
- [#450](https://github.com/plotly/dash/pull/450) Use the same prop name black list for component generation in all supported Python versions. Closes [#361](https://github.com/plotly/dash/issues/361).

## 0.28.6 - 2018-11-05
### Fixed
- [#443](https://github.com/plotly/dash/pull/443) `Dash.registered_paths` changed to a `collections.defaultdict(set)`, was appending the same package paths on every index.

## 0.28.5 - 2018-10-18
### Fixed
- [#431](https://github.com/plotly/dash/pull/431) Replace windows endline when generating components class docstrings.

## 0.28.4 - 2018-10-18
### Fixed
- [#430](https://github.com/plotly/dash/pull/430) Fix `Component.traverse()` and `Component.traverse_with_paths()` for components with `children` of type `tuple`, not just `list`.

## 0.28.3 - 2018-10-17
### Fixed
- [#418](https://github.com/plotly/dash/pull/418) Fix http-equiv typo
- Include missing polyfills to restore Internet Explorer support, restore whatwg-fetch [renderer#87](https://github.com/plotly/dash-renderer/issues/87)

## 0.28.2 - 2018-10-05
### Changed
- [#377](https://github.com/plotly/dash/pull/377) Move `add_url` function definition out of `Dash.__init__`

## 0.28.1 - 2018-09-26
### Fixed
- [#407](https://github.com/plotly/dash/pull/407) Missing favicon package_data from setup.py

## 0.28.0 - 2018-09-26
### Added
- [#406](https://github.com/plotly/dash/pull/406) Default favicon for dash apps.
- Bust the cache of the assets favicon.

### Fixed
- [#403](https://github.com/plotly/dash/pull/403) Remove the first and last blank lines from the HTML index string.

## 0.27.0 - 2018-09-20
### Added
- [#369](https://github.com/plotly/dash/pull/369), [renderer#77](https://github.com/plotly/dash-renderer/pull/77) Allow serving dev bundles from the components suite, enable with `app.run_server(dev_tools_serve_dev_bundles=True)`

### Fixed
- [#350](https://github.com/plotly/dash/pull/350) Use HTML5 syntax for the meta tag

## 0.26.6 - 2018-09-19
### Fixed
- [#387](https://github.com/plotly/dash/pull/387) Add `Cache-Control` headers to files served by `Dash.serve_component_suites`, and time modified query string to collected components suites resources.
- [#394](https://github.com/plotly/dash/pull/394) Add `InvalidResourceError` error and a Flask error handler so unregistered paths in `serve_component_suites` return a 404 instead of 500.

## 0.26.5 - 2018-09-10
### Fixed
- [#374](https://github.com/plotly/dash/pull/374) Fix `get_asset_url` with a different `assets_url_path`.

## 0.26.4 - 2018-08-28
### Fixed
- Set `url_base_pathname` to `None` in `Dash.__init__`. Fix [#364](https://github.com/plotly/dash/issues/364)

## 0.26.3 - 2018-08-27
### Added
- `Dash.get_asset_url` will give the prefixed url for the asset file.

### Fixed
- [#351](https://github.com/plotly/dash/pull/351) Prefix assets files with `requests_pathname_prefix`.

## 0.26.2 - 2018-08-26
### Fixed
- [#343](https://github.com/plotly/dash/pull/343) Only create the assets blueprint once for apps that provide the same flask instance to multiple dash instances.

## 0.26.1 - 2018-08-26
### Fixed
- [#336](https://github.com/plotly/dash/pull/336) Fix bug in `_validate_layout` which would not let a user set `app.layout` to be a function that returns a layout [(fixes #334)](https://github.com/plotly/dash/issues/334).

## 0.26.0 - 2018-08-20
### Added
- [#318](https://github.com/plotly/dash/pull/318) Add `assets_ignore` init keyword, regex filter for the assets files.

## 0.25.1 - 2018-08-20
### Fixed
- [#335](https://github.com/plotly/dash/pull/335) Ensure CSS/JS external resources are loaded before the assets.

## 0.25.0 - 2018-08-14
### Added
- [#322](https://github.com/plotly/dash/pull/322) Take config values from init or environ variables (Prefixed with `DASH_`).

### Fixed
- Take `requests_pathname_prefix` config when creating scripts tags.
- `requests/routes_pathname_prefix` must start and end with `/`.
- `requests_pathname_prefix` must end with `routes_pathname_prefix`. If you supplied both `requests` and `routes` pathname before this update, make sure `requests_pathname_prefix` ends with the same value as `routes_pathname_prefix`.
- `url_base_pathname` sets both `requests/routes` pathname, cannot supply it with either `requests` or `routes` pathname prefixes.

## 0.24.2 - 2018-08-13
### Fixed
- [#320](https://github.com/plotly/dash/pull/320) Disallow duplicate component ids in the initial layout.

## 0.24.1 - 2018-08-10
### Fixed
- Fix bug [#321](https://github.com/plotly/dash/issues/321) where importing Dash components with no props would result in an error.
- Fix a bug in 0.23.1 where importing components with arguments that are Python keywords could cause an error. In particular, this fixes `dash-html-components` with Python 3.7.

## 0.24.0 - 2018-08-10
### Added
- [#319](https://github.com/plotly/dash/pull/309) Add a modified time query string to assets included in the index in order to bust the cache.

## 0.23.1 - 2018-08-02
### Added
- [#316](https://github.com/plotly/dash/pull/316) Add `ie-compat` meta tag to the index by default.
- [#305](https://github.com/plotly/dash/pull/305) Add `external_script` and `external_css` keywords to dash `__init__`.
- Dash components are now generated at build-time and then imported rather than generated when a module is imported. This should reduce the time it takes to import Dash component libraries, and makes Dash compatible with IDEs.

## 0.22.1 - 2018-08-01
### Fixed
- [#273](https://github.com/plotly/dash/pull/273) Raise a more informative error if a non-JSON-serializable value is returned from a callback.

## 0.22.0 - 2018-07-25
### Added
- [#286](https://github.com/plotly/dash/pull/286) Asset files & index customization.
- [#294](https://github.com/plotly/dash/pull/294) Raise an error if there is no layout present when the server is run.
- [renderer#55](https://github.com/plotly/dash-renderer/pull/55) Add `_dash-error` class to the "Error loading layout" and "Error loading dependencies" messages.

### Fixed
- Attempting to render a `Boolean` value to the page no longer crashes the app.
- [renderer#57](https://github.com/plotly/dash-renderer/issues/57) If a callback references an `id` which does not exist in the DOM tree at the time it is executed, throw a more informative front-end exception.
- [renderer#54](https://github.com/plotly/dash-renderer/pull/54) Previously, if a component called `updateProps` with multiple properties, Dash would fire the callback multiple times (once for each property). Now the callback only fires once.

## 0.21.1 - 2018-04-10
### Added
- [#237](https://github.com/plotly/dash/pull/237) Support `aria-*` and `data-*` attributes in all dash html components. These new keywords can be added using a dictionary expansion, e.g. `html.Div(id="my-div", **{"data-toggle": "toggled", "aria-toggled": "true"})`
- [renderer#45](https://github.com/plotly/dash-renderer/pull/45) Allow user to choose between React versions '15.4.2' and '16.2.0':
```python
import dash_renderer

# Set the react version before setting up the Dash application
dash_renderer._set_react_version('16.2.0')

app = dash.Dash(...)
```

### Fixed
- [renderer#50](https://github.com/plotly/dash-renderer/pull/50) Update MANIFEST.in to include `react` and `react-dom` bundles for development mode

## 0.21.0 - 2018-02-21
### Added
- [#207](https://github.com/plotly/dash/pull/207) Support React components using [Flow](https://flow.org/en/docs/react/) types. `component_loader` now has the following behavior to create docstrings as determined in discussion in [#187](https://github.com/plotly/dash/issues/187):
  1. If a Dash component has `PropTypes`-generated typing, the docstring uses the `PropTypes`, _regardless of whether the component also has Flow types (current behavior)._
  2. Otherwise if a Dash component has Flow types but _not `PropTypes`_, the docstring now uses the objects generated by `react-docgen` from the Flow types.

### Fixed
- [renderer#42](https://github.com/plotly/dash-renderer/pull/42) Fix [renderer#41](https://github.com/plotly/dash-renderer/issues/41) and [renderer#44](https://github.com/plotly/dash-renderer/issues/44).
  - In some cases, during initialization, callbacks may fired multiple times instead of just once. This only happens in certain scenarios where outputs have overlapping inputs and those inputs are leaves (they don't have any inputs of their own).
  - If an output component is returned from a callback and its inputs were _not_ returned from the same input (i.e. they were already visible), then the callback to update the output would not fire. This has now been fixed. A common scenario where this app structure exists is within a Tabbed app, where there are global controls that update each tab's contents and the tab's callback just displays new output containers.

## 0.20.0 - 2018-01-19
### Added
- [#190](https://github.com/plotly/dash/pull/190) `exceptions.PreventUpdate` can be raised inside a callback to prevent the callback from updating the app. See <https://community.plotly.com/t/improving-handling-of-aborted-callbacks/7536/2>.

### Removed
- Removes logging from redux middleware from production build based on process.env.NODE_ENV.

### Changed
- Many pylint style fixes: [#163](https://github.com/plotly/dash/pull/163), [#164](https://github.com/plotly/dash/pull/164), [#165](https://github.com/plotly/dash/pull/165), [#166](https://github.com/plotly/dash/pull/166), [#167](https://github.com/plotly/dash/pull/167), [#168](https://github.com/plotly/dash/pull/168), [#169](https://github.com/plotly/dash/pull/169), [#172](https://github.com/plotly/dash/pull/172), [#173](https://github.com/plotly/dash/pull/173), [#181](https://github.com/plotly/dash/pull/181), [#185](https://github.com/plotly/dash/pull/185), [#186](https://github.com/plotly/dash/pull/186), [#193](https://github.com/plotly/dash/pull/193)
- [#184](https://github.com/plotly/dash/pull/184) New integration test framework.
- [#174](https://github.com/plotly/dash/pull/174) Submodules are now imported into the `dash` namespace for better IDE completion.

## 0.19.0 - 2017-10-16
### Changed
- 🔒 Remove CSRF protection measures. CSRF-style attacks are not relevant to Dash apps. Dash's API uses `POST` requests with content type `application/json` which are not susceptible to unwanted requests from 3rd party sites. See [#141](https://github.com/plotly/dash/issues/141).
- 🔒 `app.server.secret_key` is no longer required since CSRF protection was removed. Setting `app.server.secret_key` was difficult to document and a very common source of confusion, so it's great that users won't get bitten by this anymore :tada:
- 🐞 [renderer#22](https://github.com/plotly/dash-renderer/pull/22), [renderer#28](https://github.com/plotly/dash-renderer/pull/28) Previously, old requests could override new requests if their response was longer than the new one. This caused subtle bugs when apps are deployed on multiple processes or threads with component callbacks that update at varying rates like urls. Originally reported in [#133](https://github.com/plotly/dash/issues/133). This fix should also improve performance when many updates happen at once as outdated requests will get dropped instead of updating the UI. Performance issue with the first PR reported in [renderer#27](https://github.com/plotly/dash-renderer/issues/27) and fixed in the second PR.
- [renderer#21](https://github.com/plotly/dash-renderer/pull/21) Fix an issue where a callback would be fired excessively. Previously, the callback would be called as many times as it had inputs. Now, it is called less.

## 0.18.3 - 2017-09-08
### Added
- `app.config` is now a `dict` instead of a class. You can set config variables with `app.config['suppress_callback_exceptions'] = True` now. The previous class-based syntax (e.g. `app.config.suppress_callback_exceptions`) has been maintained for backwards compatibility.
- 🐌 Experimental behaviour for a customizable "loading state". When a callback is in motion, Dash now appends a `<div class="_dash-loading-callback"/>` to the DOM. Users can style this element using custom CSS to display loading screen overlays. This feature is in alpha, we may remove it at any time.

### Fixed
- Fix a bug from 0.18.2 that removed the ability for dash to serve the app on any route besides `/`.
- Fix a bug from 0.18.0 with the new config variables when used in a multi-app setting, causing config to be shared across apps. Originally reported in <https://community.plotly.com/t/flask-endpoint-error/5691/7>
- Rename config setting `supress_callback_exceptions` to `suppress_callback_exceptions`. The original spelling is kept for backward compatibility.
- 🐞 (renderer) Fix a bug where Dash would fire updates for each parent of a grandchild node that shared the same grandparent. Originally reported in <https://community.plotly.com/t/specifying-dependency-tree-traversal/5080/5>
- 🐞 (renderer) Fix a bug where the document title that displays "Updating..." wouldn't change if the callback raised an Exception. Now it will be removed on any response, even a failure.

## 0.18.2 - 2017-09-07
### Added
- [#70](https://github.com/plotly/dash/pull/70) 🔧 Add an `endpoint` to each of the URLs to allow for multiple routes.

## 0.18.1 - 2017-09-07
### Fixed
- [#128](https://github.com/plotly/dash/pull/128) 🐛 If `app.layout` is a function, then it used to be called excessively. Now it is called just once on startup and just once on page load.

## 0.18.0 - 2017-09-07
### Changed
- 🔒 Remove the `/static/` folder and endpoint that is implicitly initialized by flask. This is too implicit for my comfort level: I worry that users will not be aware that their files in their `static` folder are accessible
- ⚡️ Remove all API calls to the Plotly API (<https://api.plotly.com/>), the authentication endpoints and decorators, and the associated `filename`, `sharing` and `app_url` arguments. This was never documented or officially supported. Authentication has been moved to the [`dash-auth` package](https://github.com/plotly/dash-auth).
- [#107](https://github.com/plotly/dash/pull/107) ✏️ Sort prop names in exception messages.

### Added
- 🔧 Add two new `config` variables: `routes_pathname_prefix` and `requests_pathname_prefix` to provide more flexibility for API routing when Dash apps are run behind proxy servers. `routes_pathname_prefix` is a prefix applied to the backend routes and `requests_pathname_prefix` prefixed in requests made by Dash's front-end. `dash-renderer==0.8.0rc3` uses these endpoints.
- [#112](https://github.com/plotly/dash/pull/112) 🔧 Add `id` to `KeyError` exceptions in components.

### Fixed
- ✏️ Fix a typo in an exception.
- 🔧 Replaced all illegal characters in environment variables.

### 🔧 Maintenance
- 📝 Update README.md
- ✅ Fix CircleCI tests. Note that the [`dash-renderer`](https://github.com/plotly/dash-renderer) contains the bulk of the integration tests.
- 💄 Flake8 fixes and tests (fixes [#99](https://github.com/plotly/dash/issues/99))
- ✨ Add this CHANGELOG.md.

## 0.17.3 - 2017-06-22
✨ This is the initial open-source release of Dash.
