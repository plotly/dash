# Change Log for dash-html-components
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## Unreleased

## [0.10.0] - 2018-04-03
### Added
- Previously, if a user named their app file `dash.py`, an unhelpful error
message would be raised. Now, `import dash_html_components` will check if
the user has a file named `dash.py` and warn the users appropriately.
https://github.com/plotly/dash-html-components/pull/39

## [0.9.0] - 2018-02-11
### Changed
- Moved `PropTypes` import from using `react` to using `prop-types` package to support using React 16+ in `dash-renderer`

### Added
- Added `Picture` and `Base` components
- Added `muted` property to `Audio` component

## [0.8.0] - 2017-09-29
### Added
- A `key` property has been added to every component. See https://reactjs.org/docs/lists-and-keys.html for more about this attribute.

## [0.7.0] - 2017-07-18
### Added
- A `n_clicks` property has been added to every component that gets incremented automatically when the element has been clicked on

## [0.2.3] - 2016-07-20
### Fixed
- `style` propType is now correctly set to object, not string

## [0.2.2] - 2016-07-17
### Fixed
- Issue with component metadata path in pypi package

## [0.2.0] - 2016-07-07
### Added
- Fix issues with attribute casing

## 0.1.0 - 2016-06-28
- Initial release

[0.2.3]: https://github.com/plotly/dash-html-components/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/plotly/dash-html-components/compare/v0.2.0...v0.2.2
[0.2.0]: https://github.com/plotly/dash-html-components/compare/v0.1.0...v0.2.0
