# Change Log for dash-html-components
### NOTE: as of v2.0, changes in dash-html-components are all being recorded in the main dash changelog.
### This file is kept only for historical purposes.
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [1.1.4] - 2021-07-09

### Changed
- [#194](https://github.com/plotly/dash-html-components/pull/194) Updated dependencies and build process
- [#190](https://github.com/plotly/dash-core-components/pull/190) Updated R package vignettes and `dash-info.yaml` to regenerate examples without attaching now-deprecated core component packages (`dashHtmlComponents`, `dashCoreComponents`, or `dashTable`).

## [1.1.3] - 2021-04-08
### Fixed
- [#179](https://github.com/plotly/dash-html-components/pull/179) - Fixes [#77](https://github.com/plotly/dash-html-components/issues/77) Added `allow` and `referrerPolicy` properties to `html.Iframe`

- [#178](https://github.com/plotly/dash-html-components/pull/178) - Fix [#161](https://github.com/plotly/dash-html-components/issues/161) <object> `data` property, and fix [#129](https://github.com/plotly/dash-html-components/issues/129) obsolete, deprecated, and discouraged elements. No elements were removed, but comments were added to the documentation about these elements detailing their limitations.

## [1.1.2] - 2021-01-19
### Fixed
- [#169](https://github.com/plotly/dash-html-components/pull/169) - part of fixing dash import bug https://github.com/plotly/dash/issues/1143

## [1.1.1] - 2020-09-03
- Dash.jl Julia component generation

## [1.1.0] - 2020-08-25
### Added
- [#165](https://github.com/plotly/dash-html-components/pull/165) Add support for Dash.jl Julia component generation.

## [1.0.3] - 2020-04-01
### Updated
- Update generated props
- Update generated R artifacts

## [1.0.2] - 2019-11-14
### Fixed
- [#143](https://github.com/plotly/dash-html-components/pull/143) Fix IE11 compatibility issues and ES5 compatibility and validation

## [1.0.1] - 2019-08-27
### Updated
- Generated documentation

## [1.0.0] - 2019-06-20
### Added
- [#119](https://github.com/plotly/dash-html-components/pull/119)
    - Added `formEncType`, `formMethod`, `formTarget` attributes to Button
    - Added `autoComplete` attribute to Select

### Removed
- [#113](https://github.com/plotly/dash-html-components/pull/113) Removed `version.py` - use `__version__` in the main namespace.

## [0.16.0] - 2019-04-25
### Fixed
- [#110](https://github.com/plotly/dash-html-components/pull/110), [#111](https://github.com/plotly/dash-html-components/pull/111) Improved the property definitions in advance of the Dev Tools property validation.
    In particular:
    - Boolean properties like `hidden` accept a bool or a case insensitive string with the same name (e.g. `'hidden'` or `'HIDDEN'`)
    - Numeric properties like `rows`, `max`, `min` allow a stringified number or a number

### Added
- Added `formNoValidate` & `inputMode` properties.

## [0.15.0] - 2019-03-25
### Changed
- Remove undefined `setProps` handling [#103](https://github.com/plotly/dash-html-components/pull/103)

## [0.14.0] - 2019-03-04
### Added
- Added `data-dash-is-loading` attribute to all components, that holds the new `loading_state.is_loading` prop.

## [0.13.5] - 2019-01-11
### Changed
- Added `.idea`, `tests`, `dist`, `.circleci` to npmignore.
- Added repository url and long_description to setup.py
- Merged in `dashHtmlComponents` R package and updated to 0.13.5

### Removed
- Removed click events - these have been obsolete since 0.7.0 [#89](https://github.com/plotly/dash-html-components/pull/89)

## [0.13.4] - 2018-12-17
### Fixed
- Fix build from wrong dash version.

## [0.13.3] - 2018-12-17
### Fixed
- `n_clicks`/`n_clicks_timestamp` PropType changed from invalid `integer` to `number`.
- omit `n_clicks`/`n_clicks_timestamp` from wrapped element props.

## [0.13.2] - 2018-09-21
### Fixed
- Fixes Python3.7 incompatibility with `0.13.0` and `0.13.1`.

### Changed
- Regenerated classes with Python3.7 to remove `async` keyword.

## [0.13.1] - 2018-09-20
### Fixed
- Renamed `__init__.py` external_path to dash_html_components.min.js

## [0.13.0] - 2018-09-20
### Added
- Unminified dev bundle support. [#64](https://github.com/plotly/dash-html-components/pull/64)

## Unreleased

## [0.12.0] - 2018-06-01
### Changed
- `dash_html_components/__init__.py` now imports from Python class files rather than generating classes at runtime,
adding support for IDE auto complete etc.

## [0.11.0] - 2018-06-01
### Added
- A `n_clicks_timestamp` property was added to all of the components. This property represents the date that the element was clicked on and can be used to determine _which element was clicked on_ in callbacks with multiple elements. This is considered a stop-gap solution: ultimately we'll want a solution that works for _all_ properties across all components, not just the `n_clicks` property. https://github.com/plotly/dash-html-components/pull/45

## [0.10.1] - 2018-04-29
### Added
- `aria-*` and `data-*` attributes are now supported in all dash html components [#40](https://github.com/plotly/dash-html-components/pull/40)
    These new keywords can be added using a dictionary expansion, e.g.
    ```
    html.Div(id="my-div", **{"data-toggle": "toggled", "aria-toggled": "true"})
    ```
- The `role` attribute was added to all components
- The `autoComplete` property was added to `textarea`

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
