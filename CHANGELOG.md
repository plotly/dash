# Change Log for dash-renderer
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [0.12.0] - 2018-02-11
### Added
- `dash_renderer.REACT_VERSION` allows user to now choose between '15.4.2' and '16.2.0' for the React version used by Dash.

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
