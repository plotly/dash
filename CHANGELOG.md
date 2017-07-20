# Change Log for dash-renderer
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [0.7.4] - 2017-07-20
### Removed
- Remove unofficial support for `/routes`. This was never officially supported and was an antipattern in Dash. URLs and multi-page apps can be specified natively through the `dash_core_components.Link` and `dash_core_components.Location` components. See [https://plot.ly/dash/urls](https://plot.ly/dash/urls) for more details.

## [0.7.3] - 2017-06-20
### Added
- Added a class `_dash-undo-redo` to the undo/redo toolbar. This allows the undo/redo to be styled (or even removed)
