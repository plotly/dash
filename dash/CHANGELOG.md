## Unreleased

### Added
- [#944](https://github.com/plotly/dash/pull/944)
  - relevant `dash.testing` methods can now be called with either an element or a CSS selector: `select_dcc_dropdown`, `multiple_click`, `clear_input`, `zoom_in_graph_by_ratio`, `click_at_coord_fractions`.
  - Three new `dash.testing` methods: `clear_local_storage`, `clear_session_storage`, and `clear_storage` (to clear both together)
- [#937](https://github.com/plotly/dash/pull/937) `dash.testing` adds two APIs `zoom_in_graph_by_ratio` and `click_at_coord_fractions` about advanced interactions using mouse `ActionChain`
- [#938](https://github.com/plotly/dash/issues/938) Adds debugging traces to dash backend about serving component suites, so we can use it to verify the installed packages whenever in doubt.

## [1.3.1] - 2019-09-19
### Changed
- Bumped dash-core-components version from 1.2.0 to [1.2.1](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#120---2019-09-19)

## [1.3.0] - 2019-09-17
### Added
- [#923](https://github.com/plotly/dash/pull/923) Adds one configuration `--percy-assets` in `pytest` to specify extra application assets path if needed

- [#918](https://github.com/plotly/dash/pull/918) Adds `wait_for_element_by_id` and `visit_and_snapshot` APIs in browser, adds `raw_command` option (it also has higher priority than
the default waitress one) and optional `start_timeout` argument to handle large application within process runner

### Changed
- Bumped dash-table version from 4.2.0 to [4.3.0](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#430---2019-09-17)
- Bumped dash-core-components version from 1.1.2 to [1.2.0](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#120---2019-09-17)
- Bumped dash-renderer version from 1.0.1 to [1.1.0](https://github.com/plotly/dash/blob/master/dash-renderer/CHANGELOG.md#110---2019-09-17)

### Fixed
- [#915](https://github.com/plotly/dash/issues/915) Fixes `dash-generate-components` on Windows
- [#829](https://github.com/plotly/dash/issues/829) Fixes the `--remote` pytest argument which was not effective in the code, adding a new argument `--remote-url` to support the selenium grid usage in the cloud.

## [1.2.0] - 2019-08-27
### Added
- [#860](https://github.com/plotly/dash/pull/860) Adds a new arg `dev_tools_prune_errors` to `app.run_server` and `app.enable_dev_tools`. Default `True`, tracebacks only include user code and below. Set it to `False` for the previous behavior showing all the Dash and Flask parts of the stack.

### Changed
- Bumped dash-table version from 4.1.0 to [4.2.0](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#420---2019-08-27)
- Bumped dash-core-components version from 1.1.1 to [1.1.2](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#112---2019-08-27)
- Bumped dash-html-components version from 1.0.0 to [1.0.1](https://github.com/plotly/dash-html-components/blob/master/CHANGELOG.md#101---2019-08-27)
- Bumped dash-renderer version from 1.0.0 to [1.0.1](https://github.com/plotly/dash/blob/dev/dash-renderer/CHANGELOG.md#101---2019-08-27)

## [1.1.1] - 2019-08-06
### Changed
- Bumped dash-core-components version from 1.1.0 to [1.1.1](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#111---2019-08-06)

## [1.1.0] - 2019-08-05
### Added
- [#827](https://github.com/plotly/dash/pull/827) Adds support for dashR testing using pytest framework

### Changed
- Bumped dash-table version from 4.0.2 to [4.1.0](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#410---2019-08-05)
- Bumped dash-core-components version from 1.0.0 to [1.1.0](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#110---2019-08-05)

## [1.0.2] - 2019-07-15
### Fixed
- [#821](https://github.com/plotly/dash/pull/821) Fix a bug with callback error reporting, [#791](https://github.com/plotly/dash/issues/791).

### Changed
- Bumped dash-table version from 4.0.1 to [4.0.2](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#402---2019-07-15)

## [1.0.1] - 2019-07-09
### Changed
- 💥 [#808](https://github.com/plotly/dash/pull/808) Remove strong `dash.testing` dependencies per community feedbacks.
Testing users should do `pip install dash[testing]` afterwards.

- [#805](https://github.com/plotly/dash/pull/805) Add headless mode for dash.testing, add `pytest_setup_options` hook for full configuration of `WebDriver Options`.

- Bumped dash-table version from 4.0.0 to [4.0.1](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#401---2019-07-09)

## [1.0.0] - 2019-06-20
### Changed
- 💥 [#761](https://github.com/plotly/dash/pull/761) Several breaking changes to the `dash.Dash` API:
  - Removed two obsolete constructor kwargs: `static_folder` and `components_cache_max_age`
  - Removed the misspelled `supress_callback_exceptions` fallback
  - Removed the unused `resources.config.infer_from_layout`
  - Revamped `app.config`: ALL constructor args are now stored in `config`, with three exceptions: `server`, `index_string`, and `plugins`. None of these are stored in any other instance attributes anymore.
  - Changed `hot_reload_interval` from msec to seconds, for consistency with `hot_reload_watch_interval`
  - When called from `enable_dev_tools`, `debug=True` by default. It's still `False` by default from `run_server`.

- ✨ [#744](https://github.com/plotly/dash/pull/744) Dash Testing(`dash.testing`) is introduced, read the full tutorial on http://dash.plot.ly/testing.


- [#753](https://github.com/plotly/dash/pull/753) `Component` no longer inherits `MutableMapping`, so `values`, `keys`, and more are no longer methods. This fixed an issue reported in [dcc](https://github.com/plotly/dash-core-components/issues/440) where components with certain prop names defined but not provided would cause a failure to render. During component generation we now disallow all props with leading underscores or matching a few remaining reserved words: `UNDEFINED`, `REQUIRED`, `to_plotly_json`, `available_properties`, and `available_wildcard_properties`.

- [#739](https://github.com/plotly/dash/pull/739) Allow the Flask app to be provided to Dash after object initialization. This allows users to define Dash layouts etc when using the app factory pattern, or any other pattern that inhibits access to the app object. This broadly complies with the flask extension API, allowing Dash to be considered as a Flask extension where it needs to be.

- [#774](https://github.com/plotly/dash/pull/774) Allow the Flask app to set the Dash app name if the name is not provided by users.

- [#722](https://github.com/plotly/dash/pull/722) Assets are served locally by default. Both JS scripts and CSS files are affected. This improves robustness and flexibility in numerous situations, but in certain cases initial loading could be slowed. To restore the previous CDN serving, set `app.scripts.config.serve_locally = False` (and similarly with `app.css`, but this is generally less important).

- Undo/redo toolbar is removed by default, you can enable it with `app=Dash(show_undo_redo=true)`. The CSS hack `._dash-undo-redo:{display:none;}` is no longer needed [#724](https://github.com/plotly/dash/pull/724)

- 💥[#709](https://github.com/plotly/dash/pull/709) Merge the `dash-renderer` project into the main dash repo to simplify feature dev workflow. We will keep the [deprecated one](https://github.com/plotly/dash-renderer) for archive purpose.

## [0.43.0] - 2019-05-15
### Changed
- Bumped dash-core-components version from 0.47.0 to [0.48.0](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#0480---2019-05-15)
- Bumped dash-renderer version from 0.23.0 to [0.24.0](https://github.com/plotly/dash-renderer/blob/master/CHANGELOG.md#0240---2019-05-15)
- Bumped dash-table version from 3.6.0 to [3.7.0](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#370---2019-05-15)

## [0.42.0] - 2019-04-25
### Added
- [#687](https://github.com/plotly/dash/pull/687) Dev Tools support. A new UI in the application that automatically display JavaScript & Python error messages, validates your component's properties, and displays a graph of your callback's dependencies. Only enabled in debug mode. Turn this on and off with two new config flags in `app.run_server`:
    - `dev_tools_props_check` - turn on/off property validation.
    - `dev_tools_ui` - turn on/off the UI.

## [0.41.0] - 2019-04-10
### Added
- Support for "Clientside Callbacks" - an escape hatch to execute your callbacks in JavaScript instead of Python [#672](https://github.com/plotly/dash/pull/672)
- Added `dev_tools_ui` config flag in `app.run_server` (serialized in `<script id="_dash-config" type="application/json">`)
  to display or hide the forthcoming Dev Tools UI in Dash's front-end (dash-renderer). [#676](https://github.com/plotly/dash/pull/676)
- Partial updates: leave some multi-output updates unchanged while updating others [#680](https://github.com/plotly/dash/pull/680)

## Changed
- Bumped dash-core-components version from 0.45.0 to [0.46.0](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#0460---2019-04-10)
- Bumped dash-renderer version from 0.21.0 to [0.22.0](https://github.com/plotly/dash-renderer/blob/master/CHANGELOG.md#0220---2019-04-10)

## [0.40.0] - 2019-03-25
### Changed
- Bumped dash-core-components version from 0.44.0 to [0.45.0](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#0450---2019-03-25)
- Bumped dash-html-components version from 0.14.0 to [0.15.0](https://github.com/plotly/dash-html-components/blob/master/CHANGELOG.md#0150---2019-03-25)
- Bumped dash-renderer version from 0.20.0 to [0.21.0](https://github.com/plotly/dash-renderer/blob/master/CHANGELOG.md#0210---2019-03-25)

## [0.39.0] - 2019-03-04
## Added
- Allow multiple outputs from a single callback. [#436](https://github.com/plotly/dash/pull/436)
- Support for custom javascript hooks to modify callback payloads and responses. [#367](https://github.com/plotly/dash/pull/367)
- Modify the flask response with custom cookies or headers, using `dash.callback_context.response`. [#623](https://github.com/plotly/dash/pull/623)

## Changed
- Bumped dash-core-components version from 0.43.1 to [0.44.0](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#0440---2019-03-04)
- Bumped dash-html-components version from 0.13.5 to [0.14.0](https://github.com/plotly/dash-html-components/blob/master/CHANGELOG.md#0140---2019-03-04)
- Bumped dash-renderer version from 0.19.0 to [0.20.0](https://github.com/plotly/dash-renderer/blob/master/CHANGELOG.md#0200---2019-03-04)
- Bumped dash-table version from 3.5.0 to [3.6.0](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#360---2019-03-04)

## [0.38.0] - 2019-02-25
## Fixed
- Fix missing indentation for generated metadata.json [#600](https://github.com/plotly/dash/issues/600)
- Fix missing component prop docstring error [#598](https://github.com/plotly/dash/issues/598)
- Moved `__repr__` to base component instead of being generated. [#492](https://github.com/plotly/dash/pull/492)
- Raise exception when same input & output are used in a callback [#605](https://github.com/plotly/dash/pull/605)

## Changed
- Bumped dash-table version from 3.4.0 to [3.5.0](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#350---2019-02-25)
- Bumped dash-renderer version from 0.18.0 to [0.19.0](https://github.com/plotly/dash-renderer/blob/master/CHANGELOG.md#0190---2019-02-25)

## Added
- Added components libraries js/css distribution to hot reload watch. [#603](https://github.com/plotly/dash/pull/603)
- Callback context [#608](https://github.com/plotly/dash/pull/608)
  - Know which inputs fired in a callback `dash.callback_context.triggered`
  - Input/State values by name `dash.callback_context.states.get('btn.n_clicks')`

## [0.37.0] - 2019-02-11
## Fixed
- Fixed collections.abc deprecation warning for python 3.8 [#563](https://github.com/plotly/dash/pull/563)

## Changed
- Added core libraries as version locked dependencies [#565](https://github.com/plotly/dash/pull/565)
- Bumped dash-table version from 3.3.0 to [3.4.0](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md#340---2019-02-08)
- Bumped dash-renderer version from 0.17.0 to [0.18.0](https://github.com/plotly/dash-renderer/blob/master/CHANGELOG.md#0180---2019-02-11)
- Bumped dash-core-components version from 0.43.0 to [0.43.1](https://github.com/plotly/dash-core-components/blob/master/CHANGELOG.md#0431---2019-02-11)

## [0.36.0] - 2019-01-25
## Removed
- Removed support for `Event` system. Use event properties instead, for example the `n_clicks` property instead of the `click` event, see [#531](https://github.com/plotly/dash/issues/531) for details. `dash_renderer` MUST be upgraded to >=0.17.0 together with this, and it is recommended to update `dash_core_components` to >=0.43.0 and `dash_html_components` to >=0.14.0. [#550](https://github.com/plotly/dash/pull/550)

## [0.35.3] - 2019-01-23
## Fixed
- Asset blueprint takes routes prefix into it's static path. [#547](https://github.com/plotly/dash/pull/547)
- Asset url path no longer strip routes from requests. [#547](https://github.com/plotly/dash/pull/547)
- Remove print statement from PreventUpdate error handler. [#548](https://github.com/plotly/dash/pull/548)
- Removed ComponentRegistry dist cache [#524](https://github.com/plotly/dash/pull/524)

## Changed
- `assets_folder` argument now default to 'assets' [#547](https://github.com/plotly/dash/pull/547)
- The assets folder is now always relative to the given root path of `name` argument, the default of `__main__` will get the `cwd`. [#547](https://github.com/plotly/dash/pull/547)
- No longer coerce the name argument from the server if the server argument is provided. [#547](https://github.com/plotly/dash/pull/547)

## [0.35.2] - 2019-01-11
## Fixed
- Fix typo in some exception names [#522](https://github.com/plotly/dash/pull/522)

## 0.35.1 - 2018-12-27
### Fixed
- Always skip `dynamic` resources from index resources collection. [#518](https://github.com/plotly/dash/pull/518)

## 0.35.0 - 2018-12-18
## Added
- Experimental `--r-prefix` option to `dash-generate-components`, optionally generates R version of components and corresponding R package.  [#483](https://github.com/plotly/dash/pull/483)

## 0.34.0 - 2018-12-17
## Added
- `--ignore` option to `dash-generate-components`, default to `^_`. [#490](https://github.com/plotly/dash/pull/490)

## 0.33.0 - 2018-12-10
## Added
- Added specific Dash exception types to replace generic exceptions (InvalidIndexException, DependencyException, ResourceException) [#487](https://github.com/plotly/dash/pull/487)

## 0.32.2 - 2018-12-09
## Fixed
- Fix typo in missing events/inputs error message [#485](https://github.com/plotly/dash/pull/485)

## 0.32.1 - 2018-12-07
## Changed
- Muted dash related missing props docstring from extract-meta warnings [#484](https://github.com/plotly/dash/pull/484)

## 0.32.0 - 2018-12-07
## Added
- Support for .map file extension and dynamic (on demand) loading [#478](https://github.com/plotly/dash/pull/478)

## 0.31.1 - 2018-11-29
## Fixed
- Fix `_imports_.py` indentation generation. [#473](https://github.com/plotly/dash/pull/473/files)

## 0.31.0 - 2018-11-29
## Added
- Combined `extract-meta` and python component files generation in a cli [#451](https://github.com/plotly/dash/pull/451)

## 0.30.0 - 2018-11-14
## Added
- Hot reload from the browser [#362](https://github.com/plotly/dash/pull/362)
- Silence routes logging with `dev_tools_silence_routes_logging`.

## 0.29.0 - 2018-11-06
## Added
- Added component namespaces registry, collect the resources needed by component library when they are imported instead of crawling the layout. [#444](https://github.com/plotly/dash/pull/444)

## 0.28.7 - 2018-11-05
## Fixed
- Component generation now uses the same prop name black list in all supported Python versions. Closes [#361](https://github.com/plotly/dash/issues/361). [#450](https://github.com/plotly/dash/pull/450)

## 0.28.6 - 2018-11-05
## Fixed
- `Dash.registered_paths` changed to a `collections.defaultdict(set)`, was appending the same package paths on every index. [#443](https://github.com/plotly/dash/pull/443)

## 0.28.5 - 2018-10-18
## Fixed
- Replace windows endline when generating the components classes docstring [#431](https://github.com/plotly/dash/pull/431)

## 0.28.4 - 2018-10-18
## Fixed
- The `Component.traverse()` and `Component.traverse_with_paths()` methods now work correctly for components with `children` of type `tuple` (before, this only worked for `list`s). [#430](https://github.com/plotly/dash/pull/430)

## 0.28.3 - 2018-10-17
## Fixed
- Fix http-equiv typo [#418](https://github.com/plotly/dash/pull/418)

## 0.28.2 - 2018-10-05
## Added
- Moved `add_url` function definition out of `Dash.__init__` [#377](https://github.com/plotly/dash/pull/377)

## 0.28.1 - 2018-09-26
## Fixed
- Missing favicon package_data from setup.py [#407](https://github.com/plotly/dash/pull/407)

## 0.28.0 - 2018-09-26
## Added
- Default favicon for dash apps. [#406](https://github.com/plotly/dash/pull/406#issuecomment-424821743)
- Bust the cache of the assets favicon.

## Fixed
- Remove the first and last blank lines from the HTML index string. [#403](https://github.com/plotly/dash/pull/403)

## 0.27.0 - 2018-09-20
## Added
- Added support for serving dev bundles from the components suite, enable with `app.run_server(dev_tools_serve_dev_bundles=True)` [#369](https://github.com/plotly/dash/pull/369)

## Fixed
- Use HTML5 syntax for the meta tag [#350](https://github.com/plotly/dash/pull/350)

## 0.26.6 - 2018-09-19
## Fixed
- Added `Cache-Control` headers to files served by `Dash.serve_component_suites`. [#387](https://github.com/plotly/dash/pull/387)
- Added time modified query string to collected components suites resources.
- Added `InvalidResourceError`. [#393](https://github.com/plotly/dash/pull/393)
- Added a flask errorhandler to catch `InvalidResourceError` from `serve_component_suites` and return a 404.

## 0.26.5 - 2018-09-10
## Fixed
- Fix `get_asset_url` with a different `assets_url_path`. [#374](https://github.com/plotly/dash/pull/374)

## 0.26.4 - 2018-08-28
## Fixed
- Set `url_base_pathname` to `None` in `Dash.__init__`. Fix [#364](https://github.com/plotly/dash/issues/364)

## 0.26.3 - 2018-08-27
## Fixed
- Prefix assets files with `requests_pathname_prefix`. [#351](https://github.com/plotly/dash/pull/351)

## Added
- `Dash.get_asset_url` will give the prefixed url for the asset file.

## 0.26.2 - 2018-08-26
## Fixed
- Only create the assets blueprint once for app that provide the same flask instance to multiple dash instance. [#343](https://github.com/plotly/dash/pull/343)

## 0.26.1 - 2018-08-26
## Fixed
- Fix bug in `_validate_layout` which would not let a user set `app.layout` to be a function that returns a layout [(fixes #334)](https://github.com/plotly/dash/issues/334). [#336](https://github.com/plotly/dash/pull/336)

## 0.26.0 - 2018-08-20
## Added
- Added `assets_ignore` init keyword, regex filter for the assets files. [#318](https://github.com/plotly/dash/pull/318)

## 0.25.1 - 2018-08-20
## Fixed
- Ensure CSS/JS external resources are loaded before the assets. [#335](https://github.com/plotly/dash/pull/335)

## 0.25.0 - 2018-08-14
## Added
- Take configs values from init or environ variables (Prefixed with `DASH_`). [#322](https://github.com/plotly/dash/pull/322)

## Fixed
- Take `requests_pathname_prefix` config when creating scripts tags.
- `requests/routes_pathname_prefix` must starts and end with `/`.
- `requests_pathname_prefix` must ends with `routes_pathname_prefix`. If you supplied both `requests` and `routes` pathname before this update, make sure `requests_pathname_prefix` ends with the same value as `routes_pathname_prefix`.
- `url_base_pathname` set both `requests/routes` pathname, cannot supply it with either `requests` or `routes` pathname prefixes.


## 0.24.2 - 2018-08-13
## Fixed
- Disallow duplicate component ids in the initial layout. [#320](https://github.com/plotly/dash/pull/320)

## 0.24.1 - 2018-08-10
## Fixed
- Fixed bug in 0.23.1 where importing Dash components with no props would result in an error. (Fixes [#321](https://github.com/plotly/dash/issues/321)).
- Fixed bug in 0.23.1 where importing components with arguments that are python keywords could cause an error. In particular, this fixes `dash-html-components` while using Python 3.7.

## 0.24.0 - 2018-08-10
## Added
- Add a modified time query string to the assets included in the index in order to bust the cache. [#319](https://github.com/plotly/dash/pull/309)


## 0.23.1 - 2018-08-02
## Added
- Add ie-compat meta tag to the index by default. [#316](https://github.com/plotly/dash/pull/316)
- Add `external_script` and `external_css` keywords to dash `__init__`. [#305](https://github.com/plotly/dash/pull/305)
- Dash components are now generated at build-time and then imported rather than generated when a module is imported. This should reduce the time it takes to import Dash component libraries, and makes Dash compatible with IDEs.

## 0.22.1 - 2018-08-01
## Fixed
- Raise a more informative error if a non JSON serializable value is returned from a callback [#273](https://github.com/plotly/dash/pull/273)

## 0.22.0 - 2018-07-25
## Added
- Assets files & index customization [#286](https://github.com/plotly/dash/pull/286)
- Raise an error if there is no layout present when the server is running [#294](https://github.com/plotly/dash/pull/294)


## 0.21.1 - 2018-04-10
## Added
- `aria-*` and `data-*` attributes are now supported in all dash html components. (#40)
- These new keywords can be added using a dictionary expansion, e.g. `html.Div(id="my-div", **{"data-toggle": "toggled", "aria-toggled": "true"})`

## 0.21.0 - 2018-02-21
## Added
- #207 Dash now supports React components that use [Flow](https://flow.org/en/docs/react/).
    To support Flow, `component_loader` now has the following behavior to create docstrings
    as determined in discussion in [#187](https://github.com/plotly/dash/issues/187):
        1. If a Dash component has `PropTypes`-generated typing, the docstring uses the `PropTypes`, _regardless of whether the component also has Flow types (current behavior)._
        2. Otherwise if a Dash component has Flow types but _not `PropTypes`_, the docstring now uses the objects generated by `react-docgen` from the Flow types.

## 0.20.0 - 2018-01-19
## Added
- `exceptions.PreventUpdate` can be raised inside a callback to elegantly prevent
the callback from updating the app. See https://community.plot.ly/t/improving-handling-of-aborted-callbacks/7536/2 for context
and #190 for the PR.

## Changed
- Many pylint style fixes.
  See #163, #164, #165, #166, #167, #168, #169, #172, #173, #181, #185, #186, #193
- New integration test framework #184
- Submodules are now imported into the `dash` namespace for better IDE completion #174

# 0.19.0 - 2017-10-16
## Changed
- 🔒  CSRF protection measures were removed as CSRF style attacks are not relevant
to Dash apps. Dash's API uses `POST` requests with content type
`application/json` which are not susceptible to unwanted requests from 3rd
party sites. See https://github.com/plotly/dash/issues/141 for more.
- 🔒  Setting `app.server.secret_key` is no longer required since CSRF protection was
removed. Setting `app.server.secret_key` was difficult to document and
a very common source of confusion, so it's great that users won't get bitten
by this anymore :tada:

# 0.18.3 - 2017-09-08
## Added
- `app.config` is now a `dict` instead of a class. You can set config variables with
  `app.config['suppress_callback_exceptions'] = True` now. The previous class-based
  syntax (e.g. `app.config.suppress_callback_exceptions`) has been maintained for
  backwards compatibility

## Fixed
- 0.18.2 introduced a bug that removed the ability for dash to serve the app on
  any route besides `/`. This has been fixed.
- 0.18.0 introduced a bug with the new config variables when used in a multi-app setting.
  These variables would be shared across apps. This issue has been fixed.
  Originally reported in https://community.plot.ly/t/flask-endpoint-error/5691/7
- The config setting `supress_callback_exceptions` has been renamed to
  `suppress_callback_exceptions`. Previously, `suppress` was spelled wrong.
  The original config variable is kept for backwards compatibility.

# 0.18.3rc1 - 2017-09-08
The prerelease for 0.18.3

# 0.18.2 - 2017-09-07
## Added
- 🔧 Added an `endpoint` to each of the URLs to allow for multiple routes (https://github.com/plotly/dash/pull/70)

# 0.18.1 - 2017-09-07
## Fixed
- 🐛 If `app.layout` was supplied a function, then it used to be called excessively. Now it is called just once on startup and just once on page load. https://github.com/plotly/dash/pull/128

# 0.18.0 - 2017-09-07
## Changed
- 🔒  Removes the `/static/` folder and endpoint that is implicitly initialized by flask. This is too implicit for my comfort level: I worry that users will not be aware that their files in their `static` folder are accessible
- ⚡️  Removes all API calls to the Plotly API (https://api.plot.ly/), the authentication endpoints and decorators, and the associated `filename`, `sharing` and `app_url` arguments. This was never documented or officially supported and authentication has been moved to the [`dash-auth` package](https://github.com/plotly/dash-auth)
- ✏️ Sorts the prop names in the exception messages (#107)

## Added
- 🔧 Add two new `config` variables: `routes_pathname_prefix` and `requests_pathname_prefix` to provide more flexibility for API routing when Dash apps are run behind proxy servers. `routes_pathname_prefix` is a prefix applied to the backend routes and `requests_pathname_prefix` prefixed in requests made by Dash's front-end. `dash-renderer==0.8.0rc3` uses these endpoints.
- 🔧 Added id to KeyError exception in components (#112)


## Fixed
- ✏️  Fix a typo in an exception
- 🔧 Replaced all illegal characters in environment variable

##🔧 Maintenance
- 📝  Update README.md
- ✅  Fix CircleCI tests. Note that the [`dash-renderer`](https://github.com/plotly/dash-renderer) contains the bulk of the integration tests.
- 💄 Flake8 fixes and tests (fixes #99 )
- ✨ Added this CHANGELOG.md

# 0.17.3 - 2017-06-22
✨ This is the initial open-source release of Dash
