# Change Log for dash-renderer
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

# Unreleased
### Fixed
- [#944](https://github.com/plotly/dash/pull/944) fixed bug with persistence being toggled on/off on an existing component

## [1.1.0] - 2019-09-17
### Added
- [#903](https://github.com/plotly/dash/pull/903) enables props edited by the user to persist across recreating the component or reloading the page. Components need to define three new props: `persistence`, `persisted_props`, and `persistence_type` as described in the lead comment of `src/persistence.js`. App developers then enable this behavior by, in the simplest case, setting `persistence: true` on the component. First use case is table, see [dash-table#566](https://github.com/plotly/dash-table/pull/566)

### Fixed
- Reduced about 55% of the dash-renderer packages size on **PyPI** by removing the source maps. To do more advanced debugging, the source maps needs to be generated from source code with `npm run build:local` and pip install in editable mode, i.e. `pip install -e .` [#910](https://github.com/plotly/dash/pull/910)

## [1.0.1] - 2019-08-27
- Clean all the binary assets in dash-renderer repo, add tool to build all the required bundles from fresh source code to avoid confusion of the assets and improve the release process. [#874](https://github.com/plotly/dash/pull/874)

  fixes [#868](https://github.com/plotly/dash/pull/868) and [#734](https://github.com/plotly/dash/pull/734)

## [1.0.0] - 2019-06-20
### Changed
- Undo/redo toolbar is removed by default, unless `config.show_undo_redo=true` is provided. The CSS hack `._dash-undo-redo:{display:none;}` is no longer needed [#175](https://github.com/plotly/dash-renderer/pull/175)

## [0.24.0] - 2019-05-15
### Fixed
- Fix regression on handling PreventUpdate (204 NO CONTENT) [#170](https://github.com/plotly/dash-renderer/pull/170)

## [0.23.0] - 2019-04-25
### Fixed
- Fix regression for `children=0` case [#148](https://github.com/plotly/dash-renderer/issues/148)

### Added
- Dash Dev Tools [#100](https://github.com/plotly/dash-renderer/pull/100)
    - A simple UI interface, which consolidates both frontend and backend errors into an "error popup" at the top-right corner
    - Callback function visualization through a DAG(Directed Acyclic Graph) [#144](https://github.com/plotly/dash-renderer/pull/144)
    - Free [Component property validation](https://reactjs.org/docs/typechecking-with-proptypes.html) for all Dash React Components inside dash-renderer

## [0.22.0] - 2019-04-10
### Added
- Added support for clientside callbacks [#143](https://github.com/plotly/dash-renderer/pull/143)

### Changed
[#145](https://github.com/plotly/dash-renderer/pull/145)
- Update from React 15.4.2 to React 16.8.6

### Removed
- `dash_renderer._set_react_version` support for 15.4.2 and 16.2.0

## [0.21.0] - 2019-03-25
### Changed
[#140](https://github.com/plotly/dash-renderer/pull/140)
[#126](https://github.com/plotly/dash-renderer/pull/126)
- Optimize rendering
- Always assign `setProps` to components

## [0.20.0] - 2019-03-04
### Added
- Loading states API [#267](https://github.com/plotly/dash/issues/267)

## [0.19.0] - 2019-02-25
## Added
- Added which properties fired to update prop request. [#124](https://github.com/plotly/dash-renderer/pull/124)

## [0.18.0] - 2019-02-11
### Removed
- Removed redux logger for the dev. [#118](https://github.com/plotly/dash-renderer/pull/118)

## [0.17.0] - 2019-01-25
### Removed
- Obsolete Event system [#114](https://github.com/plotly/dash-renderer/pull/114)

## [0.16.2] - 2019-01-11
### Fixed
[#110](https://github.com/plotly/dash-renderer/pull/110)
- Keep the config store state on soft reload.
- AppProvider returns `Loading...` if no configs as before #108

### Removed - 2018-12-17
- Unused login api and Authentication component [#108](https://github.com/plotly/dash-renderer/pull/108)

## [0.16.1] - 2018-12-14
### Fixed
- Added `key` to rendered components, fixing [#379](https://github.com/plotly/dash-core-components/issues/379)

## [0.16.0] - 2018-12-07
### Added
- [Redux devtools](https://github.com/zalmoxisus/redux-devtools-extension) support [#107](https://github.com/plotly/dash-renderer/pull/107)

## [0.15.2] - 2018-12-07
### Added
- Source map [#104](https://github.com/plotly/dash-renderer/issues/104)
    Related Dash issue [#480](https://github.com/plotly/dash/issues/480)

## [0.15.1] - 2018-11-17
### Fixed
- Fix a bug in the ON_PROP_CHANGE callback where history was not correctly set when acting on more than one component. In particular, the 'undo' button should now work as expected. Fixes [#66](https://github.com/plotly/dash-renderer/issues/66).

## [0.15.0] - 2018-11-14
### Added
- Hot reload [#73](https://github.com/plotly/dash-renderer/pull/73)

## [0.14.3] - 2018-10-11
### Fixed
- Included missing polyfills to restore Internet Explorer support [#87](https://github.com/plotly/dash-renderer/issues/87)

## [0.14.2] - 2018-10-11
### Fixed
- Upgraded dependencies to remove warnings
- Restored whatwg-fetch [#87](https://github.com/plotly/dash-renderer/issues/87)
### Added
- Prettier support
- Better ESLint configs

## [0.14.1] - 2018-09-20
### Fixed
- Renamed `__init__.py` external_path to dash_renderer.min.js

## [0.14.0] - 2018-09-20
### Added
- Unminified dev bundle support. [#77](https://github.com/plotly/dash-renderer/pull/77)

## [0.13.2] - 2018-07-24
### Fixed
- Attempting to render a `Boolean` value to the page no longer crashes the app.

## [0.13.1] - 2018-07-18
### Fixed
- If a callback references an `id` which does not exist in the DOM tree at the time it is executed, throw an informative front-end exception (previously an uninformative front-end exception was thrown). https://github.com/plotly/dash-renderer/issues/57

## [0.13.0] - 2018-06-01
### Fixed
- Previously, if a component called `updateProps` with multiple properties, Dash would fire the callback multiple times (once for each property). Now, the callback is only fired once. https://github.com/plotly/dash-renderer/pull/54


### Added
- A `_dash-error` class was added to the "Error loading layout" and "Error loading dependencies" messages. https://github.com/plotly/dash-renderer/pull/55

## [0.12.1] - 2018-03-29
### Fixed
- Updates MANIFEST.in to include react and react-dom bundles for development mode
https://github.com/plotly/dash-renderer/pull/50

## [0.12.0] - 2018-03-28
### Added
- Allows user to now choose between '15.4.2' and '16.2.0' for React versions
```python
import dash_renderer

# Set the react version before setting up the Dash application
dash_renderer._set_react_version('16.2.0')

app = dash.Dash(...)
```
https://github.com/plotly/dash-renderer/pull/45

## [0.11.3] - 2018-02-01
### Fixed
- Fixed #41 in #42. In some cases, during initialization, callbacks may fired multiple times instead of just once. This only happens in certain scenarios where outputs have overlapping inputs and those inputs are leaves (they don't have any inputs of their own). See #41 for a simple example and #42 for some more extensive test cases.
- Fixed #44 in #42. If an output component is returned from a callback and its inputs were _not_ returned from the same input (i.e. they were already visible), then the callback to update the output would not fire. This has now been fixed. A common scenario where this app structure exists is within a Tabbed app, where there are global controls that update each tab's contents and the tab's callback just displays new output containers. See #44 for a simple example and #42 for some more extensive test cases.

## [0.11.2] - 2018-01-08
### Fixed
- Removes logging from redux middleware from production build based on process.env.NODE_ENV.

## [0.11.1] - 2017-10-19
### Fixed
- :snail: :racehorse: Fixed a performance issue. In 0.11.0 we introduced an  internal request queue to fix some bugs. This request queue was boundless and in certain cases it could become really large and slow down the app. Now, we remove old requests from this queue when they are no longer needed, keeping its size under control. Originally reported in https://github.com/plotly/dash-renderer/issues/27

## [0.11.0] - 2017-09-28
### Fixed
- 🐞 Previously, old requests could override new requests if their response was longer than the new one.
This caused subtle bugs when apps are deployed on multiple processes or threads with component
callbacks that update at varying rates like urls. Originally reported in github.com/plotly/dash/issues/133. This fix should also improve performance when many updates happen at once as outdated requests will get dropped instead of updating the UI.

## [0.10.0] - 2017-09-19
### Fixed
- Fixed an issue where a callback would be fired on page load and when dynamically generated excessively. Previously, the callback would be called as many times as it had inputs. Now, it is called less. https://github.com/plotly/dash-renderer/pull/21
### Maintenance
- Add percy screenshot tests



## [0.9.0] - 2017-09-07
### Fixed
- 🐞 Fixed a bug where Dash would fire updates for each parent of a grandchild node that shared the same grandparent. Originally reported in https://community.plot.ly/t/specifying-dependency-tree-traversal/5080/5
- 🐞 Fixed a bug where the document title that displays "Updating..." wouldn't change if the callback raised an Exception. Now it will be removed on any response, even a failure.

### Added
- 🐌 Experimental behaviour for a customizable "loading state". When a callback is in motion, Dash now appends a `<div class="_dash-loading-callback"/>` to the DOM.
Users can style this element using custom CSS to display loading screen overlays.
This feature is in alpha, we may remove it at any time.

## [0.8.0] - 2017-09-07
### Added
- 🔧 Added support for the `requests_pathname_prefix` config parameter introduced in `dash==0.18.0`

## [0.7.4] - 2017-07-20
### Removed
- Remove unofficial support for `/routes`. This was never officially supported and was an antipattern in Dash. URLs and multi-page apps can be specified natively through the `dash_core_components.Link` and `dash_core_components.Location` components. See [https://plot.ly/dash/urls](https://plot.ly/dash/urls) for more details.

## [0.7.3] - 2017-06-20
### Added
- Added a class `_dash-undo-redo` to the undo/redo toolbar. This allows the undo/redo to be styled (or even removed)
