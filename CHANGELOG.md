# Change Log for dash-renderer
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [0.11.0rc1] - 2017-09-27
### Fixed
- 🐞 Previously, old requests could override new requests if their response was longer than the new one.
This caused subtle bugs when apps are deployed on multiple processes or threads with component
callbacks that update at varying rates like urls. Originally reported in github.com/plotly/dash/issues/133


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
