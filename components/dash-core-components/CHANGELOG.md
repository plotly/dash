# Change Log for dash-core-components
### NOTE: as of v2.0, changes in dash-core-component are all being recorded in the main dash changelog.
### This file is kept only for historical purposes.
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [1.17.1] - 2021-07-12

### Fixed

- Removed unnecessary Julia files from npm package


## [1.17.0] - 2021-07-09

### Fixed

- [#963](https://github.com/plotly/dash-core-components/pull/963) Fixes [#885](https://github.com/plotly/dash-core-components/issues/885)

  This applies the fix from [#878](https://github.com/plotly/dash-core-components/pull/878) to the RangeSlider.
  It not only fixes the bug where the tooltips were visible when slider was not, but it also reduces the lag in the
  tooltip when the slider handles are moved.

### Updated
- [#939](https://github.com/plotly/dash-core-components/pull/939) Upgrade Plotly.js to v2.2.1. Note that this is a major version upgrade to Plotly.js, however we are not treating this as a breaking change for DCC as the majority of breaking changes in Plotly.js do not affect the Dash API. The one exception is that several trace types that have long been deprecated are removed entirely.
  - [Major release 2.0.0](https://github.com/plotly/plotly.js/releases/tag/v2.0.0):
    - Stop exporting d3 as `Plotly.d3`, and remove many other deep pieces of the public API. This does not affect the `dcc.Graph` component, but if you make use of `Plotly` from the global scope in some other way you may be affected.
    - Drop the deprecated trace types `contourgl` and `area`, as well as legacy pre-`scatterpolar` polar attributes `bar.r`, `bar.t`, `scatter.r`, `scatter.t`, `layout.radialaxis`, `layout.angularaxis`. Use `scatterpolar`, `barpolar`, and `polar` subplots instead.
    - `heatmapgl` and `pointcloud` trace types, and the `transform` attribute are deprecated, and will be removed in a future release.
    - Increase CSP safety by removing function constructors. 3D plots still use function constructors, but if you place one of the non-3D bundles (including the new `strict` bundle) in your `assets` folder you will have no function constructors.
    - Remove "Aa" text in legends.
    - Default `hovermode` to "closest".
    - Default `textposition` to "auto" in `bar` traces. If you previously used the `bar.text` attribute for hover only, you will need to explicitly set `textposition="none"`.
    - Add `bar.marker.pattern`, `image.zsmooth`, and various other features and bugfixes.
  - [Feature release 2.1.0](https://github.com/plotly/plotly.js/releases/tag/v2.1.0):
    - New `icicle` trace type.
    - New `legendrank` trace attribute.
    - Several other additions and bug fixes.
  - [Feature release 2.2.0](https://github.com/plotly/plotly.js/releases/tag/v2.2.0):
    - Legend group titles
    - Half-year directive (`%h`) for date formatting
    - Several other bug fixes and performance improvements
  - [Patch release 2.2.1](https://github.com/plotly/plotly.js/releases/tag/v2.2.1) containing a security fix.

### Added
- [#932](https://github.com/plotly/dash-core-components/pull/932) Adds a new copy to clipboard component.
- [#948](https://github.com/plotly/dash-core-components/pull/948)] Adds `disabled_days` prop to `DatePickerRange` and `DatePickerSingle` components. With this prop you can specify days that should be made unselectable in the date picker, in addition to those that fall outside of the range specified by `min_date_allowed` and `max_date_allowed`.

### Changed
- [#972](https://github.com/plotly/dash-core-components/pull/972) Updated R package vignettes and `dash-info.yaml` to regenerate examples without attaching now-deprecated core component packages (`dashHtmlComponents`, `dashCoreComponents`, or `dashTable`).

## [1.16.0] - 2021-04-08
### Added
- [#863](https://github.com/plotly/dash-core-components/pull/863) Adds a new `Download` component. Along with this several utility functions are added to help construct the appropriate data format:
  - `dcc.send_file` - send a file from disk
  - `dcc.send_data_frame` - send a `DataFrame`, using one of its writer methods
  - `dcc.send_bytes` - send a bytestring or the result of a bytestring writer
  - `dcc.send_string` - send a string or the result of a string writer

### Changed
- [#923](https://github.com/plotly/dash-core-components/pull/923)
  Set `autoComplete` to off in `dcc.Dropdown`. This fixes [#808](https://github.com/plotly/dash-core-components/issues/808)

### Fixed
- [#930](https://github.com/plotly/dash-core-components/pull/930) Fixed a bug [#867](https://github.com/plotly/dash-core-components/issues/867) with `DatePickerRange` that would sometimes shift the allowed dates by one day.
- [#934](https://github.com/plotly/dash-core-components/pull/934) Fixed a bug in `EnhancedTab` component that ignored `disabled_className` property

## [1.15.0] - 2021-01-19
### Fixed
- [#905](https://github.com/plotly/dash-core-components/pull/905) Make sure the `figure` prop of `dcc.Graph` receives updates from user interactions in the graph, by using the same `layout` object as provided in the prop rather than cloning it. Fixes [#879](https://github.com/plotly/dash-core-components/issues/879).
- [#903](https://github.com/plotly/dash-core-components/pull/903) Part of fixing dash import bug https://github.com/plotly/dash/issues/1143

### Updated
- [#911](https://github.com/plotly/dash-core-components/pull/911), [#906](https://github.com/plotly/dash-core-components/pull/906)
  - Upgraded Plotly.js to [1.58.4](https://github.com/plotly/plotly.js/releases/tag/v1.58.4)
    - Patch Release [1.58.4](https://github.com/plotly/plotly.js/releases/tag/v1.58.4)
    - Patch Release [1.58.3](https://github.com/plotly/plotly.js/releases/tag/v1.58.3)

### Added
- [#888](https://github.com/plotly/dash-core-components/pull/888) Adds a `drag_value` prop to `dcc.Slider`to be able to fire callbacks from dragging and releasing the slider.

## [1.14.1] - 2020-12-09
### Updated
- [#898](https://github.com/plotly/dash-core-components/pull/898)
    - Patch Release [1.58.2](https://github.com/plotly/plotly.js/releases/tag/v1.58.2)

## [1.14.0] - 2020-12-07
### Updated
- [#889](https://github.com/plotly/dash-core-components/pull/889), [#893](https://github.com/plotly/dash-core-components/pull/893)
  - Upgraded Plotly.js to [1.58.1](https://github.com/plotly/plotly.js/releases/tag/v1.58.1)
    - Patch Release [1.58.1](https://github.com/plotly/plotly.js/releases/tag/v1.58.1)
    - [Feature release of Plotly.js 1.58.0](https://github.com/plotly/plotly.js/releases/tag/v1.58.0) which:
      - Add `ticklabelposition` attribute to cartesian axes and colorbars [#5275](https://github.com/plotly/plotly.js/pull/5275)
      - Add "strict" `autotypenumbers` to axes and `layout` [#5240](https://github.com/plotly/plotly.js/pull/5240)
      - Add `itemwidth` to legends [#5212](https://github.com/plotly/plotly.js/pull/5212)
      - Add `root.color` attribute to `sunburst` and `treemap` traces [#5232](https://github.com/plotly/plotly.js/pull/5232), [#5245](https://github.com/plotly/plotly.js/pull/5245)
      - Enable fast image rendering for all linear axes [#5307](https://github.com/plotly/plotly.js/pull/5307)
      - Rework matches and scaleanchor so they work together [#5287](https://github.com/plotly/plotly.js/pull/5287)

## [1.13.0] - 2020-10-29
### Added
- [#871](https://github.com/plotly/dash-core-components/pull/871) Add Julia syntax highlighting support for dcc.Markdown

### Fixed
- [#878](https://github.com/plotly/dash-core-components/pull/878)
  - Fixed [#751](https://github.com/plotly/dash-core-components/issues/751), a bug that causes `dcc.Slider` and `dcc.RangerSlider` tooltips to be visible even if the slider component isn't visible (e.g. overflow),

### Updated
- [#875](https://github.com/plotly/dash-core-components/pull/875)
  - Upgraded Plotly.js to [1.57.1](https://github.com/plotly/plotly.js/releases/tag/v1.57.1)
    - Patch release [1.57.1](https://github.com/plotly/plotly.js/releases/tag/v1.57.1)
    - [Feature release of Plotly.js 1.57.0](https://github.com/plotly/plotly.js/releases/tag/v1.57.0) which:
      - Add "domain" axis references in layout `images`, `shapes` and `annotations` [#5014](https://github.com/plotly/plotly.js/pull/5014)
      - Add `rotation` attribute to `sunburst` traces [#5171](https://github.com/plotly/plotly.js/pull/5171), [#5201](https://github.com/plotly/plotly.js/pull/5201)
      - Add computed margins in "full-json" export [#5203](https://github.com/plotly/plotly.js/pull/5203)
    - [Feature release of Plotly.js 1.56.0](https://github.com/plotly/plotly.js/releases/tag/v1.56.0) which:
        - Introduce period positioning attributes on date axes in various cartesian traces [#5074](https://github.com/plotly/plotly.js/pull/5074), [#5175](https://github.com/plotly/plotly.js/pull/5175)
        - Add minexponent attribute to improve control over SI prefixes in axis tick labels [#5121](https://github.com/plotly/plotly.js/pull/5121),
        - Add sort attribute to sunburst and treemap traces to disable automatic sort [#5164](https://github.com/plotly/plotly.js/pull/5164)
        - Handle rgba colors in colorscale of surface traces [#5166](https://github.com/plotly/plotly.js/pull/5166)
    - Patch release [1.55.2](https://github.com/plotly/plotly.js/releases/tag/v1.55.2)

## [1.12.1] - 2020-09-16
### Fixed
- [#854](https://github.com/plotly/dash-core-components/pull/854) Used `persistenceTransforms` to strip the time part of the datetime in the persited props of DatePickerSingle (date) and DatePickerRange (end_date, start_date), fixing [dcc#700](https://github.com/plotly/dash-core-components/issues/700).

### Added
- [#850](https://github.com/plotly/dash-core-components/pull/850) Add property `prependData` to `Graph` to support `Plotly.prependTraces`
  + refactored the existing `extendTraces` API to be a single `mergeTraces` API that can handle both `prepend` as well as `extend`.

### Updated
- [#864](https://github.com/plotly/dash-core-components/pull/864) Upgraded Plotly.js to [1.55.2](https://github.com/plotly/plotly.js/releases/tag/v1.55.2)

## [1.12.0] - 2020-09-03
### Updated
- [#858](https://github.com/plotly/dash-core-components/pull/858)
  - Upgraded Plotly.js to [1.55.1](https://github.com/plotly/plotly.js/releases/tag/v1.55.1)
  - Patch release [1.55.1](https://github.com/plotly/plotly.js/releases/tag/v1.55.1)
  - [Feature release of Plotly.js 1.55.0](https://github.com/plotly/plotly.js/releases/tag/v1.55.0) which:
    - Introduce "period" `ticklabelmode` on cartesian date axes [#4993](https://github.com/plotly/plotly.js/pull/4993), [#5055](https://github.com/plotly/plotly.js/pull/5055), [#5060](https://github.com/plotly/plotly.js/pull/5060), [#5065](https://github.com/plotly/plotly.js/pull/5065), [#5088](https://github.com/plotly/plotly.js/pull/5088), [#5089](https://github.com/plotly/plotly.js/pull/5089)
    - Add new formatting options for weeks and quarters [#5026](https://github.com/plotly/plotly.js/pull/5026)
    - Add `source` attribute to `image` traces for fast rendering [#5075](https://github.com/plotly/plotly.js/pull/5075)
    - Add `zsmooth` attribute for discrete `heatmapgl` traces [#4953](https://github.com/plotly/plotly.js/pull/4953)
    - Add horizontal and vertical markers for arrow charts [#5010](https://github.com/plotly/plotly.js/pull/5010)
    - Add touch support to `rangeslider` [#5025](https://github.com/plotly/plotly.js/pull/5025)

## [1.11.0] - 2020-08-25
### Added
- [#851](https://github.com/plotly/dash-core-components/pull/851) Add support for Dash.jl Julia built components
- [#840](https://github.com/plotly/dash-core-components/pull/840) Add styling properties to `dcc.Loading` component
  + `parent_className`: Add CSS class for the outermost `dcc.Loading` parent div DOM node
  + `parent_style`: Add CSS style property for the outermost `dcc.Loading` parent div DOM node
  + provides a workaround for the previous behaviour the of `className` property, which changed in [#740](https://github.com/plotly/dash-core-components/pull/740). `parent_className` (or inline styles in `parent_style`) now allow CSS rules to be applied to the outermost `dcc.Loading` div, which is no longer covered by `className` on loading completion as of Dash Core Components `>= 1.9.1` (Dash `>= 1.11.0`).

## [1.10.2] - 2020-07-27
- [#835](https://github.com/plotly/dash-core-components/pull/835)
  - Upgraded Plotly.js to [1.54.7](https://github.com/plotly/plotly.js/releases/tag/v1.54.7)
    - Patch release [1.54.7](https://github.com/plotly/plotly.js/releases/tag/v1.54.7)
    - Patch release [1.54.6](https://github.com/plotly/plotly.js/releases/tag/v1.54.6)
    - Patch release [1.54.5](https://github.com/plotly/plotly.js/releases/tag/v1.54.5)
    - Patch release [1.54.4](https://github.com/plotly/plotly.js/releases/tag/v1.54.4)

## [1.10.1] - 2020-06-17
### Updated
- [#824](https://github.com/plotly/dash-core-components/pull/824)
  - Upgraded plotly.js to [1.54.3](https://github.com/plotly/plotly.js/releases/tag/v1.54.3)
    - Patch release [1.54.3](https://github.com/plotly/plotly.js/releases/tag/v1.54.3)
    - Patch release [1.54.2](https://github.com/plotly/plotly.js/releases/tag/v1.54.2)

## [1.10.0] - 2020-05-05
### Changed
- [#793](https://github.com/plotly/dash-core-components/pull/793) Added title key (i.e. HTML `title` attribute) to option dicts in `dcc.Dropdown` `options[]` list property.

### Fixed
- [#792](https://github.com/plotly/dash-core-components/pull/792) Improved the robustness of `dcc.Store` components, fixing [#456](https://github.com/plotly/dash-core-components/issues/456) whereby persistent storage could become corrupted, and fixing lifecycle issues that prevented adding `Store` components to the page after initial loading.
- [#790](https://github.com/plotly/dash-core-components/pull/790) Fixed bug where the dcc.Dropdown dropdown was hidden by the dash_table.DataTable fixed rows and columns.

### Updated
- [#800](https://github.com/plotly/dash-core-components/pull/800)
  - Upgraded plotly.js to [1.54.1](https://github.com/plotly/plotly.js/releases/tag/v1.54.1)
  - [Feature release of Plotly.js 1.54.0](https://github.com/plotly/plotly.js/releases/tag/v1.54.0) which:
    - Introduces new drag modes "drawline", "drawrect", "drawcircle", "drawopenpath", "drawclosedpath", adds optional modebar buttons for drawing & removing new shapes inside cartesian subplots, adds newshape and activeshape attributes to layout, and adds editable and fillrule attributes to layout.shapes[#4775](https://github.com/plotly/plotly.js/pull/4775)
  - Add angle and allowoverlap attributes to marker of scattermapbox traces[#4575](https://github.com/plotly/plotly.js/pull/4575), [#4794](https://github.com/plotly/plotly.js/pull/4794)
  - Also contains various other fixes

## [1.9.1] - 2020-04-10
### Changed
- [#740](https://github.com/plotly/dash-core-components/pull/740) Keep components that are loading in the DOM, but not visible, as opposed to removing them entirely. This will ensure that the size of the component's container does not shrink or expand when the component goes into the loading state.

### Fixed
- [#740](https://github.com/plotly/dash-core-components/pull/740) Fixed bug in which mapbox `uirevision` was not behaving when inside a `dcc.Loading` component

## [1.9.0] - 2020-04-01
### Changed
- [#766](https://github.com/plotly/dash-core-components/pull/766) Update from React 16.8.6 to 16.13.0
- [#768](https://github.com/plotly/dash-core-components/pull/768) Added title property to dcc.Link
- [#776](https://github.com/plotly/dash-core-components/pull/776) Update dcc.Link to set href as children if children not defined. Makes href a required prop as well.
- [#767](https://github.com/plotly/dash-core-components/pull/767) Updated dcc.Link to respond to click modifiers, and added a target prop.
- [#774](https://github.com/plotly/dash-core-components/pull/774) Fixed dcc.Location firing callbacks for wrong property.
- [772](https://github.com/plotly/dash-core-components/pull/772) Modified dcc.Link to work with absolute paths if refresh=True.

### Updated
- [#784](https://github.com/plotly/dash-core-components/pull/784)
  - [Feature release of Plotly.js 1.53.0](https://github.com/plotly/plotly.js/releases/tag/v1.53.0) which contains:
    - `rangebreaks` on date axes [#4614](https://github.com/plotly/plotly.js/pull/4614)
    - (x|y) unified `hovermode` [#4620](https://github.com/plotly/plotly.js/pull/4620)
    - "hovered data" mode to `spikesnap` [#4665](https://github.com/plotly/plotly.js/pull/4665)
    - "full-json" export format to `Plotly.toImage` and `Plotly.dowloadImage` [#4593](https://github.com/plotly/plotly.js/pull/4593)
    - node.customdata and link.customdata in `sankey` traces [#4621](https://github.com/plotly/plotly.js/pull/4621)
    - `opacityscale` for `surface` traces [#4480](https://github.com/plotly/plotly.js/pull/4480)

## [1.8.1] -2020-02-27
### Added
- [#760](https://github.com/plotly/dash-core-components/pull/760) Added R examples to package help

### Changed
- [#762](https://github.com/plotly/dash-core-components/pull/762) Renamed async modules with hyphen `-` instead of tilde `~`

## [1.8.0] - 2020-02-04
### Changed
- [#743](https://github.com/plotly/dash-core-components/pull/743) Location component now emits an event on URL path update from Link component
- [#739](https://github.com/plotly/dash-core-components/pull/739) Async Slider and RangeSlider
- [#729](https://github.com/plotly/dash-core-components/pull/729) Handle case where dcc fails to load when used inside an iframe with a sandbox attribute that only has allow-scripts

### Fixed
- [#730](https://github.com/plotly/dash-core-components/pull/730) Fixed bug in which input components with type `number` did not correctly update their values.
- [#731](https://github.com/plotly/dash-core-components/pull/731) Fixed bug where non-clearable dropdowns could still be cleared by typing backspace

### Updated
- [#747](https://github.com/plotly/dash-core-components/pull/747)
  - Upgrade plotly.js to [1.52.2](https://github.com/plotly/plotly.js/releases/tag/v1.52.2)

## [1.7.1] - 2020-01-15 (JS-only)
### Fixed
- [#734](https://github.com/plotly/dash-core-components/pull/734) Fix JS-facing release bug where `Plotly.js` was listed in `devDependencies` instead of `dependencies`

## [1.7.0] - 2020-01-14
### Added
- [#711](https://github.com/plotly/dash-core-components/pull/711) Added support for `dcc.Link` (dccLink) and nested `dcc.Markdown` (dccMarkdown) react components inside of `dcc.Markdown`
- [#706](https://github.com/plotly/dash-core-components/pull/706)
  - Added new `responsive` property that overrides the underlying Plotly.js graph responsiveness from Dash-land
  - Added responsiveness on graph parent element resize (previously only worked on window.resize)
  - Added new `dash-graph--pending` class to dcc.Graph, present while resizing, (re-)rendering, loading

### Changed
- [#723](https://github.com/plotly/dash-core-components/pull/723) Changed npm package content to allow source code inclusion from other projects
- [#725](https://github.com/plotly/dash-core-components/pull/725) Improve async graph performance by parallelizing resource fetching instead of fetching sequentially
- [#720](https://github.com/plotly/dash-core-components/pull/720) `highlight.js` is now bundled into the package, and no longer sets the `window.hljs` variable. Similarly to how `plotly.js` is handled, it is overridden by a user-provided version if one exists.

### Updated
- [#732](https://github.com/plotly/dash-core-components/pull/732)
  - Upgraded plotly.js to [1.52.1](https://github.com/plotly/plotly.js/releases/tag/v1.52.1)
  - [Feature release 1.52.0](https://github.com/plotly/plotly.js/releases/tag/v1.52.0) which contains:
    - Enable loading locale bundles before plotly.js bundles [#4453](https://github.com/plotly/plotly.js/pull/4453)
    - `ko` localization [#4315](https://github.com/plotly/plotly.js/pull/4315)
  - Patch release [1.52.1](https://github.com/plotly/plotly.js/releases/tag/v1.52.1) containing several bug fixes.
- [#706](https://github.com/plotly/dash-core-components/pull/706)
  - Upgraded plotly.js to [1.51.3](https://github.com/plotly/plotly.js/releases/tag/v1.51.3)

## [1.6.0] - 2019-11-27
### Updated
- Upgraded plotly.js to 1.51.2 [#708](https://github.com/plotly/dash-core-components/pull/708)
  - Patch release [1.51.2](https://github.com/plotly/plotly.js/releases/tag/v1.51.2) containing several bug fixes.

### Changed
- [#695](https://github.com/plotly/dash-core-components/pull/695) Improvements to Slider and RangeSlider
  - Marks outside of the range specified by `min` and `max` are now omitted when the slider renders.
  - Padding is now dependent on the orientation (vertical or horizontal), and whether or not tooltips are always displayed.
  - The whitespace is now preserved for `marks` labels.

### Added
- [#695](https://github.com/plotly/dash-core-components/pull/695) Added new property `verticalHeight` to Slider and RangeSlider, to allow the user to specify the height (in px) of vertical sliders. This defaults to `400`.

## [1.5.1] - 2019-11-14
### Fixed
- [#696](https://github.com/plotly/dash-core-components/pull/696) Fix IE11 compatibility issues and ES5 compatibility and validation

### Changed
- [#687](https://github.com/plotly/dash-core-components/pull/687/) Use `start_date`, `min_date_allowed`, `end_date`, or `max_date_allowed` for the initial visible month if the value of the parameter `initial_visible_month` is not supplied.

## [1.5.0] - 2019-11-04
### Added
- [#692](https://github.com/plotly/dash-core-components/pull/692) Async DatePickerSingle, DatePickerRange, Dropdown, Markdown, Upload components

### Updated
- [#693](https://github.com/plotly/dash-core-components/pull/693) Upgraded plotly.js to 1.51.1
  - [Feature release 1.51.0](https://github.com/plotly/plotly.js/releases/tag/v1.51.0) which contains:
    - A new `image` trace type to display 3- or 4-channel color images as data
    - `automargin` for `pie` charts for better readability when labeling lots of small slices
    - Toggle-type `updatemenus`
    - `zh-CN` localization
    - And various other small features and bug fixes
  - Patch release [1.51.1](https://github.com/plotly/plotly.js/releases/tag/v1.51.1) containing several bug fixes.

## [1.4.0] - 2019-10-29
### Added
- [#616](https://github.com/plotly/dash-core-components/pull/616) Async Graph and Plotly.js

## [1.3.1] - 2019-10-17
### Updated
- Upgraded plotly.js to 1.50.1 [#681](https://github.com/plotly/dash-core-components/issues/681)
  - Patch release [1.50.1](https://github.com/plotly/plotly.js/releases/tag/v1.50.1) containing several bug fixes.

### Fixed
- [#681](https://github.com/plotly/dash-core-components/issues/681) Fix a bug with the dcc.Graph component logging errors in certain circumstances when nested inside a dcc.Loading component

## [1.3.0] - 2019-10-08
### Added
- Added `search_value` prop to `Dropdown`, for server-side options loading/filtering. [#660](https://github.com/plotly/dash-core-components/pull/660)

### Updated
- Upgraded plotly.js to 1.50.0 [#675](https://github.com/plotly/dash-core-components/pull/675)
  - [Feature release 1.50.0](https://github.com/plotly/plotly.js/releases/tag/v1.50.0) which contains:
    - A new `treemap` trace type for display of hierarchical data.
    - `texttemplate` support for all traces with on-graph text, and custom date formatting for templated on-graph and hover text.
    - Transitions (animation) for `bar` charts.
    - Numerous other performance improvements, features, and bug fixes.
  - Patch release [1.49.5](https://github.com/plotly/plotly.js/releases/tag/v1.49.5) containing several bug fixes.

## [1.2.1] - 2019-09-19
### Fixed
- Fix regression in DatePickerRange, DatePickerSingle, Input
[#652](https://github.com/plotly/dash-core-components/issues/652)


## [1.2.0] - 2019-09-17
### Added
- Added support for persistence of user-edited props to value-input components: `Checklist`, `DatePickerRange`, `DatePickerSingle`, `Dropdown`, `Input`, `RadioItems`, `RangeSlider`, `Slider`, `Tabs`, and `Textarea`. New props are `persistence`, `persistence_type`, and `persisted_props`. Set `persistence` to a truthy value to enable, the other two modify persistence behavior. See [plotly/dash#903](https://github.com/plotly/dash/pull/903) for more details. [#646](https://github.com/plotly/dash-core-components/pull/646)

### Fixed
- Fixed `Slider` and `RangeSlider` components with `tooltip.always_visible` [#640](https://github.com/plotly/dash-core-components/issues/640)

- Fixed an infinite loop problem when `Graph` is wrapped by `Loading` component [#608](https://github.com/plotly/dash-core-components/issues/608)

## [1.1.2] - 2019-08-27
### Fixed
- Fixed problems with `Graph` components leaking events and being recreated multiple times if declared with no ID [#604](https://github.com/plotly/dash-core-components/pull/604)

- Fixed problem with `DatePickerRange` component about `clearable` not working [#614](https://github.com/plotly/dash-core-components/issues/614) and [#594](https://github.com/plotly/dash-core-components/issues/594)

### Updated
- Upgraded plotly.js to 1.49.4 [#612](https://github.com/plotly/dash-core-components/issues/612)
  - Patch releases [1.49.4](https://github.com/plotly/plotly.js/releases/tag/v1.49.4), [1.49.3](https://github.com/plotly/plotly.js/releases/tag/v1.49.3), [1.49.2](https://github.com/plotly/plotly.js/releases/tag/v1.49.2)


## [1.1.1] - 2019-08-06
### Updated
- Upgraded plotly.js to 1.49.1 [#595](https://github.com/plotly/dash-core-components/issues/595)
  - Patch release [1.49.1](https://github.com/plotly/plotly.js/releases/tag/v1.49.1)

## [1.1.0] - 2019-08-05
### Changed
- Fixed inconsistent behavior of `input` with `type=number` [#580](https://github.com/plotly/dash-core-components/pull/580)

### Updated
- Upgraded plotly.js to 1.49.0 [#589](https://github.com/plotly/dash-core-components/pull/589)
  - [Feature release 1.49.0](https://github.com/plotly/plotly.js/releases/tag/v1.49.0) which contains:
    - New `indicator` trace type for gauge and KPI displays.
    - Lots of tile map improvements: `choroplethmapbox` and `densitymapbox` trace types, numerous `style` options for `mapbox` subplots that do not require a Mapbox access token, and more.
    - Various bug fixes and smaller improvements.

## [1.0.0] - 2019-06-20
### Added
- `Markdown` components support code highlighting - no need to switch to `SyntaxHighlighter`, which has been removed. Use triple backticks, with the opening backticks followed by the language name or abbreviation. [#562](https://github.com/plotly/dash-core-components/pull/562) Supported languages:
    - Bash
    - CSS
    - HTTP
    - JavaScript
    - Python
    - JSON
    - Markdown
    - HTML, XML
    - R
    - Ruby
    - SQL
    - Shell Session
    - YAML
- Added a `dedent` prop to `Markdown` components, and enabled it by default - removing all matching leading whitespace from every line that has any non-whitespace content. You can disable this with `dedent=False`. [#569](https://github.com/plotly/dash-core-components/pull/569)
- Ability to add tooltips to `Slider` and `RangeSlider`, which can be visible always or on hover. Tooltips also take a position argument. [#564](https://github.com/plotly/dash-core-components/pull/564)

### Fixed
- Fixed `min_date_allowed` and `max_date_allowed` bug in `DatePickerRange` [#551](https://github.com/plotly/dash-core-components/issues/551)
- Fixed unwanted `resize()` calls on unmounted `Graph`s [#534](https://github.com/plotly/dash-core-components/issues/534)
- Fixed `tab--disabled` CSS class issue in `Tab` component with custom styling [#568](https://github.com/plotly/dash-core-components/pull/568)

### Changed
- Changed `dcc.Checklist` prop `values` to `value`, to match all the other input components [#558](https://github.com/plotly/dash-core-components/pull/558). Also improved prop types for `Dropdown` and `RadioItems` `value` props to consistently accept both strings and numbers.

### Removed
- 💥 Removed the `SyntaxHighlighter` component. This is now built into `Markdown` [#562](https://github.com/plotly/dash-core-components/pull/562).
- Removed the `containerProps` prop in `Markdown` - after the refactor of [#562](https://github.com/plotly/dash-core-components/pull/562), its function is served by the `id`, `className`, and `style` props. [#569](https://github.com/plotly/dash-core-components/pull/569)
- Removed `version.py` - use `__version__` in the main namespace instead. [#555](https://github.com/plotly/dash-core-components/pull/555)

### Updated
- Upgraded plotly.js to 1.48.3 [#571](https://github.com/plotly/dash-core-components/pull/571)
  - [Feature release 1.48.0](https://github.com/plotly/plotly.js/releases/tag/v1.48.0) which contains:
    - New `funnel` and `funnelarea` trace types
    - Shared color axes and colorbars
    - Sorting cartesian axes by the value on the opposite axis
    - Improvements to `bar` & `waterfall` text, legend clicking, histogram binning, hover text, and more
  - Patch releases [1.48.3](https://github.com/plotly/plotly.js/releases/tag/v1.48.3), [1.48.2](https://github.com/plotly/plotly.js/releases/tag/v1.48.2), [1.48.1](https://github.com/plotly/plotly.js/releases/tag/v1.48.1), [1.47.4](https://github.com/plotly/plotly.js/releases/tag/v1.47.4), [1.47.3](https://github.com/plotly/plotly.js/releases/tag/v1.47.3), [1.47.2](https://github.com/plotly/plotly.js/releases/tag/v1.47.2), [1.47.1](https://github.com/plotly/plotly.js/releases/tag/v1.47.1) containing numerous bug fixes

## [0.48.0] - 2019-05-15
### Added
- `figure` prop in `dcc.Graph` now accepts a `frames` key
- Improved the `Dropdown` options description for dash-docs [#547](https://github.com/plotly/dash-core-components/pull/547)
- Added `optionHeight` prop to `Dropdown` [#552](https://github.com/plotly/dash-core-components/pull/552)
- Merged in R `dashCoreComponents` package and updated to 0.48.0

### Removed
- Removed unused `key` prop from `dcc.ConfirmDialog`

## [0.47.0] - 2019-04-25
### Fixed
- Fixed style regression in DatePickerSingle and DatePickerRange [#518](https://github.com/plotly/dash-core-components/issues/518)
- **Breaking** - In `dcc.Input`, fixed several HTML properties that weren't properly camel cased and therefore were not actually applied in the DOM [#523](https://github.com/plotly/dash-core-components/pull/523/):
    - `autocomplete` is now `autoComplete`
    - `autofocus` is now `autoFocus`
    - `inputmode` is now `inputMode`
    - `maxlength` is now `maxLength`
    - `minlength` is now `minLength`
- Improved property definitions of various components in anticipation of upcoming component validation (https://github.com/plotly/dash-renderer/pull/100/). [#523](https://github.com/plotly/dash-core-components/pull/523/)
- **Breaking** - `n_blur_timestamp` & `n_submit_timestamp` in `Input` & `Textarea` is now a number instead of a date object/string. This matches the form of `n_clicks_timestamp` as used in `dash_html_components`. [#523](https://github.com/plotly/dash-core-components/pull/523/)
- Fixed an issue with `ConfirmDialog` that could display multiple confirm popups instead of a single popup in certain contexts. [#523](https://github.com/plotly/dash-core-components/pull/523/)
- `dcc.Markdown` `containerProps` is now applied to the component's container again. This was broken in 0.45.0's `react-markdown` upgrade.

### Changed
- `dcc.Interval` will reset its timer when re-enabled. Previously, if the `dcc.Interval` was disabled, it's "clock would keep running": when it was reenabled, it would fire at the next `interval` on the previous clock's schedule, rather than `interval` milliseconds later. For example, previously the schedule might look like this:
    ```
    0 seconds: interval started with `interval=5000`
    5 seconds: `n_intervals=1`
    7 seconds: callback sets `disabled=True`
    10 seconds: interval continues to run, but doesn't fire an update
    13 seconds: callback sets `disabled=False`
    15 seconds: interval fires an update: `n_intervals=2`
    ```

    Now, it will look like this:
    ```
    0 seconds: interval started with `interval=5000`
    5 seconds: `n_intervals=1`
    7 seconds: callback sets `disabled=True` - interval stops
    13 seconds: callback sets `disabled=False` - clock resets
    18 seconds: interval fires an update: `n_intervals=2`
    ```

## [0.46.0] - 2019-04-10
### Added
- `extendData` prop for `Graph` component. This feeds `Plotly.extendTraces` for incremental data updates. [#461](https://github.com/plotly/dash-core-components/pull/461)

### Changed
[#508](https://github.com/plotly/dash-core-components/pull/508)
- Upgrade from React 15.4.2 to 16.8.6
- Upgrade from react-date 12.3.0 to 20.1.0

### Fixed
- Fix unnecessary `loading_state` prop for `Input` component. [#498](https://github.com/plotly/dash-core-components/issues/498)
- Ensure `DatePickerSingle` callbacks fire with cleared dates. [#511](https://github.com/plotly/dash-core-components/pull/511)
- Fixes incorrect default values for `config` prop of `Graph`. [#515](https://github.com/plotly/dash-core-components/pull/515)

### Updated
- Upgraded plotly.js to 1.47.0 [#516](https://github.com/plotly/dash-core-components/pull/516)
  - [Feature release 1.47.0](https://github.com/plotly/plotly.js/releases/tag/v1.47.0) which contains:
    - New `volume` gl3d trace type
    - Interactive node grouping for Sankey diagrams, using box or lasso selection
    - Add way for Plotly.toImage and Plotly.downloadImage to export images with current graph width/height by passing width/height option as null
    - Improvements to hover labels, legends, and more
  - [Feature release 1.46.0](https://github.com/plotly/plotly.js/releases/tag/v1.46.0) which contains:
    - New `waterfall` trace type
    - New `sunburst` trace type
    - Implement connectgaps on surface traces
    - Implement hovertemplate for box and violin points
    - Display hover labels above modebar, ensuring that the hover labels are always visible within the graph div
  - Patch releases [1.46.1](https://github.com/plotly/plotly.js/releases/tag/v1.46.1), [1.45.3](https://github.com/plotly/plotly.js/releases/tag/v1.45.3), [1.45.2](https://github.com/plotly/plotly.js/releases/tag/v1.45.2), and [1.45.1](https://github.com/plotly/plotly.js/releases/tag/v1.45.1) containing numerous bug fixes

## [0.45.0] - 2019-03-25
### Added
- `restyleData` prop for `Graph` component [#483](https://github.com/plotly/dash-core-components/pull/483)

### Changed
- `dcc.Markdown` now uses GitHub-flavored markdown instead of CommonMark markdown. This was done as part of upgrading `react-markdown` third party library from 2.4.5 to [4.0.6](https://github.com/rexxars/react-markdown/blob/master/CHANGELOG.md#406---2019-01-04). Compare the differences in these online editors: [CommonMark editor](https://spec.commonmark.org/dingus/), [GitHub Markdown Editor](https://rexxars.github.io/react-markdown/). Notable changes:
    - A line break is now needed between paragraphs and lists.
    - Links are automatically rendered.
    - Many more features are supported like tables and strikethrough.

### Fixed
- Fix Vertical Slider regression [#479](https://github.com/plotly/dash/issues/479)
- Fix Slider regression [#485](https://github.com/plotly/dash/issues/485)

## [0.44.0] - 2019-03-04
### Added
- Loading component [#267](https://github.com/plotly/dash/issues/267)

### Updated
- Upgraded plotly.js to 1.45.0 [#470](https://github.com/plotly/dash-core-components/pull/470)
  - [Feature release 1.45.0](https://github.com/plotly/plotly.js/releases/tag/v1.45.0) which contains:
     - Sankey diagram improvements including circular networks, node grouping, and concentration colorscales
     - Matching cartesian axes
     - Better bar, box, and violin alignment control
     - Orthographic 3D projections
     - Hovertemplate support for more trace types, including all 3D traces
     - And many other features and bug fixes
  - Patch release [1.44.4](https://github.com/plotly/plotly.js/releases/tag/v1.44.4) containing numerous bug fixes

## [0.43.1] - 2019-02-11
### Updated
- Upgraded plotly.js to 1.44.3 [#458](https://github.com/plotly/dash-core-components/pull/458)
  - Patch releases [1.44.2](https://github.com/plotly/plotly.js/releases/tag/v1.44.2) and [1.44.3](https://github.com/plotly/plotly.js/releases/tag/v1.44.3) containing numerous bug fixes

## [0.43.0] - 2019-01-25
### Added
- Added event props `n_blur` and `n_clicks` - along with `n_blur_timestamp` and `n_clicks_timestamp` - in `Textarea` components, to maintain the functionality lost by removing the `click` and `blur` events. All other events were already covered by existing props. [#444](https://github.com/plotly/dash-core-components/pull/444)
- Merged in R `dashCoreComponents` package and updated to 0.43.0

### Fixed
- Fix dynamically disabling and enabling `Interval` components [#436](https://github.com/plotly/dash-core-components/pull/436)
- Clear date in DatePickerSingle and DatePickerRange [#434](https://github.com/plotly/dash-core-components/issues/434)

### Removed
- Removed `Event` system - see https://github.com/plotly/dash/issues/531 for details. [#444](https://github.com/plotly/dash-core-components/pull/444)

### Updated
- Upgraded plotly.js to 1.44.1 [#445](https://github.com/plotly/dash-core-components/pull/445)
  - [Feature release 1.44.0](https://github.com/plotly/plotly.js/releases/tag/v1.44.0) which contains:
    - A new `isosurface` gl3d trace type
    - Animated transitions via `Plotly.react` using `layout.transitions`
    - `hovertemplate` support in many more trace types
    - And many other features and bug fixes
  - Patch releases [1.44.1](https://github.com/plotly/plotly.js/releases/tag/v1.44.1) and [1.43.2](https://github.com/plotly/plotly.js/releases/tag/v1.43.2) containing numerous bug fixes

## [0.42.1] - 2019-01-07
### Fixed
- Fix `dcc.Store` type changes [#427](https://github.com/plotly/dash-core-components/pull/427)

## [0.42.0] - 2018-12-27
### Fixed
- Fix `dcc.Store` null values in list causing an infinite loop [#424](https://github.com/plotly/dash-core-components/pull/424)

### Updated
- Upgraded plotly.js to 1.43.1 [#423](https://github.com/plotly/dash-core-components/pull/423). This includes:
  - [Feature release 1.43.0](https://github.com/plotly/plotly.js/releases/tag/v1.43.0), which contains:
    - `multicategory` axis type for hierarchical categories
    - `uirevision` attributes to control persistence of user-driven changes to the graph
    - `hovertemplate` for more control of hover labels for certain trace types
    - Alignment options for titles and legend items
    - And many other features and bug fixes
  - Patch releases [1.43.1](https://github.com/plotly/plotly.js/releases/tag/v1.43.1), [1.42.5](https://github.com/plotly/plotly.js/releases/tag/v1.42.5), [1.42.4](https://github.com/plotly/plotly.js/releases/tag/v1.42.4), and [1.42.3](https://github.com/plotly/plotly.js/releases/tag/v1.42.3) containing numerous bug fixes

## [0.41.0] - 2018-12-11
### Added
- `dangerously_allow_html` prop for Markdown component for allowing HTML.

## [0.40.5] - 2018-12-11
### Fixed
- Fix typos in DatePickerSingle props [#361](https://github.com/plotly/dash-core-components/pull/361)

## [0.40.4] - 2018-12-10
### Fixed
- Add map files to manifest [#413](https://github.com/plotly/dash-core-components/pull/413)

## [0.40.3] - 2018-12-07
### Added
- Source map [#404](https://github.com/plotly/dash-core-components/issues/404)
    Related Dash issue [#480](https://github.com/plotly/dash/issues/480)

## [0.40.2] - 2018-12-04
### Fixed
- Put Input value set in onBlur/onSubmit under a debounce check [#384](https://github.com/plotly/dash-core-components/pull/384)

## [0.40.1] - 2018-12-04
### Fixed
- Fixed issue [#390](https://github.com/plotly/dash-core-components/issues/390) by providing better styles for vertical Tabs.

## [0.40.0] - 2018-11-28
### Added
- Add Logout button (dash-deployment-server authentication integration) [#388](https://github.com/plotly/dash-core-components/pull/388)

## [0.39.0] - 2018-11-12
### Changed
- Updated `react` and `react-dom` to version `^16.6.1`
- Updated `react-docgen` to `^2.21.0`
- Updated `react-select-fast-filter-options` to `^0.2.3`
- Updated `react-virtualized-select` to `^3.1.3`
- Upgraded `babel` and dependencies to `7.1.5`
- Upgraded `enzyme` and dependencies to `3.7.0`
- Removed `react-select` because it's unused - we're using `react-virtualized-select` instead.

## [0.38.1] - 2018-11-14
### Fixed
- The issue [#115](https://github.com/plotly/dash-core-components/issues/115)
with datepicker, which didn't appear when the date value is `None` was fixed.
By default, current month would appear in such cases for
`DatePickerRange` and `DatePickerSingle` components.
See pull request https://github.com/plotly/dash-core-components/pull/201.
- Refactored the way the Graph component would generate an unique id if none provided.
- Default CSS imported via `style-loader` is now placed at top, so that user supplied CSS can overwrite it, fixes [#380](https://github.com/plotly/dash-core-components/issues/380)

## [0.38.0] - 2018-11-07
### Fixed
- Changed the way the default CSS files for some components are loaded to being loaded with webpack instead of as dependencies.

## [0.37.2] - 2018-11-07
### Changed
- Updated `react-select` to version `2.1.0`

## [0.37.1] - 2018-11-07
### Added
- Added `clickannotation` event to `dcc.Graph`.
See https://github.com/plotly/dash-core-components/pull/182.

## [0.37.0] - 2018-11-04
### Fixed
- Some Input props weren't being picked up by React. Changed:
    - `autocomplete` to `autoComplete`
    - `autofocus` to `autoFocus`
    - `inputmode` to `inputMode`
    - `maxlength` to `maxLength`
    - `minlength` to `minLength`
### Added
- Unit tests for `Input` component.
- New `debounce` prop for `Input` component that determines if the input should update to a Dash server immediately, or on 'Enter' key. Fixes [#169](https://github.com/plotly/dash-core-components/issues/169)
### Changed
- `min` and `max` prop now won't update the input when values are lower than or greater than `min` and `max` respectively. Fixes[#173](https://github.com/plotly/dash-core-components/issues/173)
- `step` prop can now be a `number` and is therefor set correctly on the corresponding `<input/>` tag. Fixes [#292](https://github.com/plotly/dash-core-components/issues/292)

## [0.36.0] - 2018-11-01
### Fixed
- The `npm start` command now runs the Demo app again [#346](https://github.com/plotly/dash-core-components/issues/346)

## [0.36.0] - 2018-10-31
### Updated
- Upgraded plotly.js to 1.42.2 [#354](https://github.com/plotly/dash-core-components/pull/354). This includes:
  - [Feature release 1.42.0](https://github.com/plotly/plotly.js/releases/tag/v1.42.0) which contains:
    - A new trace type `parcats` (parallel categories)
    - `modebar` styling
    - `pie` trace titles
    - And many other features and bug fixes
  - Patch releases [1.42.2](https://github.com/plotly/plotly.js/releases/tag/v1.42.2) and [1.42.1](https://github.com/plotly/plotly.js/releases/tag/v1.42.1) containing numerous bug fixes

## [0.35.2] - 2018-10-30
### Fixed
- Fix Input not used in callbacks resetting the value on updates. [#350](https://github.com/plotly/dash-core-components/pull/350)

## [0.35.1] - 2018-10-29
### Fixed
- Fix Dropdown options prop docstring typo [#328](https://github.com/plotly/dash-core-components/pull/328/files)
- Fix Input readonly prop -> readOnly [#348](https://github.com/plotly/dash-core-components/pull/348)

## [0.35.0] - 2018-10-22
### Added
- n_blur/n_submit and timestamps props added to the Input component. [#326](https://github.com/plotly/dash-core-components/pull/326)

## [0.34.0] - 2018-10-17
### Added
- `npm run test-unit` will run new Jest+Enzyme unit tests
- Unit tests for Tabs component
### Fixed
- Fixed bug in Tabs component where value was resetting if using callback-less mode [#331](https://github.com/plotly/dash-core-components/issues/331)
- Fixed bug with default Tabs value not being set to children's Tab value (if it's set)
- Fixed bug where Tabs.children.props wheren't being selected properly, related to [#84](https://github.com/plotly/dash-renderer/issues/84)

## [0.33.1] -- 2018-10-17
### Fixed
- Fix Store component nested data [#333](https://github.com/plotly/dash-core-components/pull/333)

## [0.33.0] -- 2018-10-04
### Fixed
- Patched plotly.js version 1.41.3 [#320](https://github.com/plotly/dash-core-components/pull/320). This includes patch releases [1.41.3](https://github.com/plotly/plotly.js/releases/tag/v1.41.3), [1.41.2](https://github.com/plotly/plotly.js/releases/tag/v1.41.2), and [1.41.1](https://github.com/plotly/plotly.js/releases/tag/v1.41.1) containing numerous bug fixes.

## [0.32.0] - 2018-10-2
### Added
- Added Store component [#248](https://github.com/plotly/dash-core-components/pull/248)


## [0.31.0] - 2018-09-21
### Changed
- Updated NPM scripts:
  - `test` now runs Selenium integration tests
  - `format` runs Prettier formatter
  - There are new `build` scripts, most notably `build:watch` runs a watcher and rebuilds upon changes
  - There's a new `publish-all` script that publishes to NPM and PyPi
### Fixed
- The `start` script will now run the `Demo` application

## [0.30.2] - 2018-09-21
### Fixed
- Fixed regression in Graph component where it wouldn't resize correctly [#256](https://github.com/plotly/dash-core-components/issues/256)

## [0.30.1] - 2018-09-20
### Fixed
- Renamed `__init__.py` external_path to dash_core_components.min.js

## [0.30.0] - 2018-09-20
### Added
- Unminified dev bundle support. [#293](https://github.com/plotly/dash-core-components/pull/293)

## [0.29.0] -- 2018-09-13
### Updated
- Upgraded Plotly.js, the underlying library behind the `dash_core_components.Graph` component, to version 1.41.0 [#302](https://github.com/plotly/dash-core-components/pull/302). Feature release [1.41.0](https://github.com/plotly/plotly.js/releases/tag/v1.41.0) adds:
  - Stacked area charts, as part of `scatter` traces
  - A new `barpolar` trace type for polar "bar" traces. This replaces and improves the deprecated `area` trace type.
  - A `responsive` plot config option
  - And various other features and bug fixes.

  Many of these features were funded directly by companies that rely on this library. If your organization or company would like to sponsor particular features or bug fixes in these open source libraries, please reach out: http://plotly.com/products/consulting-and-oem

## [0.28.3] - 2018-09-07
### Changed
- The `Interval` component's `max_interval` prop can now be used to stop/restart the interval. Fixes [#266](https://github.com/plotly/dash-core-components/issues/266)
- The `Graph` component's `id` is now not required to be set.
### Fixed
- Fixed bug where Graph would resize randomly when rerendered, for example in a dcc.Tabs component.

## [0.28.2] - 2018-09-06
### Fixed
- Fixed bug in Tabs component where initial tab content wasn't rendering, [#282](https://github.com/plotly/dash-core-components/issues/282)
- Fixed bug in Tabs component where no default Tab is selected if Tabs.value is empty

## [0.28.1] - 2018-08-29
### Changed
- `candlestick` and `OHLC` charts are now plotted using the `Plotly.react` method instead of the `Plotly.newPlot` method.
### Fixed
- Fix bug where front-end error was thrown when setting `Graph.figure = {}` (fixes [#260]).

## [0.28.0]
### Updated
- Upgraded plotly.js to version 1.40.1 [#280](https://github.com/plotly/dash-core-components/pull/280). This includes [Feature release 1.40.0](https://github.com/plotly/plotly.js/releases/tag/v1.40.0) and patch releases [1.40.1](https://github.com/plotly/plotly.js/releases/tag/v1.40.1), [1.39.4](https://github.com/plotly/plotly.js/releases/tag/v1.39.4), [1.39.3](https://github.com/plotly/plotly.js/releases/tag/v1.39.3), and [1.39.2](https://github.com/plotly/plotly.js/releases/tag/v1.39.2), containing:
  - `contour` trace legend items
  - `piecolorway` and `extendpiecolors` attributes for more control over `pie` colors
  - And many other features and bug fixes

## [0.27.2]
### Fixed
- `Tabs.children` can now be undefined, so you can update them dynamically. [#265](https://github.com/plotly/dash-core-components/issues/265)
- `Tabs` Callback-less version no longer has the 2nd tab selected by default [#262](https://github.com/plotly/dash-core-components/issues/262)
- Fixes bug with nested `Tabs` [#273](https://github.com/plotly/dash-core-components/issues/273) and [#272](https://github.com/plotly/dash-core-components/issues/272)

## [0.27.1]
### Fixed
- `ConfirmDialogProvider` can now be used without a callback. [#241](https://github.com/plotly/dash-core-components/pull/241)
- `ConfirmDialog`, only fire `submit` when `submit` is clicked. [#242](https://github.com/plotly/dash-core-components/issues/242) fixed in [#241](https://github.com/plotly/dash-core-components/pull/241)

## [0.27.0]
### Changed
- `dash_core_components/__init__.py` now imports from python class files rather than generating classes at runtime,
adding support for IDE autocomplete etc.

## [0.26.0]
### Added
- New Tabs and Tab components! [#213](https://github.com/plotly/dash-core-components/pull/213#pullrequestreview-135893345)

## [0.25.1]
### Fixed
- `__init__` version formatting for unpkg.

## [0.25.0]
### Added
- `ConfirmDialog` and `ConfirmDialogProvider` components [#211](https://github.com/plotly/dash-core-components/pull/211)

## [0.24.1]
### Fixed
- Improved DatePickerRange, fixing issues [#209](https://github.com/plotly/dash-core-components/issues/209) and [#152](https://github.com/plotly/dash-core-components/issues/152)
- Link component now is a proper <a> tag so you can right click on it, and will scroll back to top. Fixes [#99](https://github.com/plotly/dash-core-components/issues/99), implemented in [#215](https://github.com/plotly/dash-core-components/pull/215)
- Added `max_interval` prop to `Interval` component, fixing issue [#222](https://github.com/plotly/dash-core-components/issues/222)


## [0.24.0]
### Updated
- Upgraded plotly.js, the underlying library behind the
`dash_core_components.Graph` component, to version 1.39.1 [#228](https://github.com/plotly/dash-core-components/pull/228). This includes:
  - [Feature release 1.39.0](https://github.com/plotly/plotly.js/releases/tag/v1.39.0), which contains:
    - `layout.template` capability, along with `Plotly.makeTemplate` and `Plotly.validateTemplate`.
    - A new 3D `streamtube` trace type
    - `scattergl` on-graph text
    - `polar` polygon grids
    - And many other features and bug fixes
  - Patch releases [1.39.1](https://github.com/plotly/plotly.js/releases/tag/v1.39.1), [1.38.3](https://github.com/plotly/plotly.js/releases/tag/v1.38.3), [1.38.2](https://github.com/plotly/plotly.js/releases/tag/v1.38.2), and [1.38.1](https://github.com/plotly/plotly.js/releases/tag/v1.38.1) containing numerous bug fixes.
  - Many of these features were funded directly by companies that rely on this library. If your organization or company would like to sponsor particular features or bug fixes in these open source libraries, please reach out: http://plotly.com/products/consulting-and-oem

## [0.23.0]
### Updated
- Upgraded plotly.js to version 1.38.0 [#207](https://github.com/plotly/dash-core-components/pull/207). This includes:
  - Feature releases [1.38.0](https://github.com/plotly/plotly.js/releases/tag/v1.38.0), [1.37.0](https://github.com/plotly/plotly.js/releases/tag/v1.37.0), and [1.36.0](https://github.com/plotly/plotly.js/releases/tag/v1.36.0), which contain:
    - A new 3D `cone` trace type to visualize vector fields
    - A new `splom` (aka Scatter PLOt Matrix) trace type
    - Performance improvements for `splom` and other multi-subplot graphs
    - `plotly_legendclick` and `plotly_legenddoubleclick` events
    - Multi-selection and click-to-select for `parcoords` axes
    - Fixed-size shapes
    - And many other features and bug fixes
  - Patch releases [1.37.1](https://github.com/plotly/plotly.js/releases/tag/v1.37.1) and [1.36.1](https://github.com/plotly/plotly.js/releases/tag/v1.36.1) containing numerous bug fixes

## [0.22.2] - 2018-05-22
### Fixed
- `dcc.Input` component now handles `disabled=False` property.
- Broken sourcemaps for debugging.
### Added
- Testing configuration for CHROMEPATH and SERVER_PROCESSES

## [0.22.1] - 2018-04-09
### Fixed
- Various bugs with the `ohlc` and `candlestick` chart type in the `dcc.Graph`
component were fixed. See https://github.com/plotly/dash-core-components/pull/184.

## [0.22.0] - 2018-04-03
### Added
- Previously, if a user named their app file `dash.py`, an unhelpful error
message would be raised. Now, `import dash_core_components` will check if
the user has a file named `dash.py` and warn the users appropriately.
https://github.com/plotly/dash-core-components/pull/177

## [0.21.1] - 2018-03-28
### Fixed
- In some cases, frequently multi-page apps, the `dcc.Graph` interactive properties
will stop working (`selectedData`, `hoverData`, `relayoutData`). This should be fixed now. https://github.com/plotly/dash-core-components/pull/178
- `dcc.Graph` will now resize after it it plotted for the first time. This should fix issues
where the `dcc.Graph` component was not fitting to the size of its container. https://github.com/plotly/dash-core-components/pull/178

## [0.21.0] - 2018-03-12
### Updated
- Upgraded Plotly.js, the underlying library behind the
`dash_core_components.Graph` component, to version 1.35.2 [#174](https://github.com/plotly/dash-core-components/pull/174). This includes [Feature release 1.35.0](https://github.com/plotly/plotly.js/releases/tag/v1.35.0) and patch releases [1.35.2](https://github.com/plotly/plotly.js/releases/tag/v1.35.2), [1.35.1](https://github.com/plotly/plotly.js/releases/tag/v1.35.1), which contain:
  - An `automargin` attribute for cartesian axes with long tick labels
  - Support for typed arrays as data inputs
  - layout `grid` attribute for easy subplot generation
  - And numerous other features and bug fixes

## [0.20.2] - 2018-03-05
### Fixed
- The `selectedData`, `clickData`, and `hoverData` callbacks were being attached without being
removed every time the graph was updated. They are now removed and reattached. #172

## [0.20.1] - 2018-03-01
### Fixed
- The `serve_locally` was broken - the Plotly.js bundle wasn't being served correctly.

## [0.20.0] - 2018-03-01
### Updated
- Upgraded plotly.js, the underlying library behind the
`dash_core_components.Graph` component, to version 1.34.0 [#170](https://github.com/plotly/dash-core-components/pull/170). [Feature release 1.34.0](https://github.com/plotly/plotly.js/releases/tag/v1.34.0) contains:
  - `Plotly.react`, a new do-it-all API method that creates and updates graphs using the same API signature
  - Constraint-type contours in `contour` traces
  - `notched` `box` traces
  - Localization machinery for auto-formatted date axis ticks
  - And many other features and bug fixes

## [0.19.0] - 2018-02-11
### Changed
- `PropTypes` now uses `prop-types` package instead of `React` to support move to React 16+

## [0.18.1] - 2017-01-25
### Fixed
- Patched plotly.js to version 1.33.1 [#151](https://github.com/plotly/dash-core-components/pull/151). [Patch release 1.33.1](https://github.com/plotly/plotly.js/releases/tag/v1.33.1) includes numerous bug fixes.

## [0.18.0] - 2017-01-19
### Updated
- Upgraded Plotly.js, the underlying library behind the `dash_core_components.Graph` component, to [version 1.33.0](https://github.com/plotly/plotly.js/releases/tag/v1.33.0). This was a huge release! Here are some of the new features that are available:
  - Completely rewritten `scattergl` trace type using `regl` [plotly.js#2258](https://github.com/plotly/plotly.js/pull/2258)
  - Completely rewritten polar chart renderer accompanied by new `scatterpolar` and `scatterpolargl` trace types [plotly.js#2200](https://github.com/plotly/plotly.js/pull/2200). The old polar trace types - `scatter` with `(r, t)` coordinates, bar with `(r, t)` coordinates, and `area` - are now deprecated.
  - Add the ability to draw layout images and layout shapes on subplot with `scattergl` traces [plotly.js#2258](https://github.com/plotly/plotly.js/pull/2258)
  - Add `fill` capabilities to `scattergl` traces [plotly.js#2258](https://github.com/plotly/plotly.js/pull/2258)
  - Add `spikedistance`, `hoverdistance` and `spikesnap` for more customizable spikes and hover behavior on cartesian subplots [plotly.js#2247](https://github.com/plotly/plotly.js/pull/2247)
  - Add official Spanish translation (locale `es`) [plotly.js#2249](https://github.com/plotly/plotly.js/pull/2249)
  - Add official French translation (locale `fr`) [plotly.js#2252](https://github.com/plotly/plotly.js/pull/2252)
  - And numerous other features and bug fixes
  - Many of these features were funded directly by companies that rely on this library. If your organization or company would like to sponsor particular features or bug fixes in these open source libraries, please reach out: http://plotly.com/products/consulting-and-oem

## [0.17.1] - 2017-01-18
### Fixed
- Previously, if `None` is supplied to `SyntaxHighlighter` or `Markdown`, the
component would not render and the app would break. This is problematic because
if `children` isn't supplied (as done in the case for when you are updating that
property from a callback), `None` is the default property. Fixes https://github.com/plotly/dash-core-components/issues/147. This bug was introduced in
v0.15.4.

## [0.17.0] - 2017-01-11
### Added
- The `dcc.Graph` component now includes `pointNumbers` inside `selectedData`
and `hoverData` if the chart type is a `histogram`, `histogram2d`, or `histogram2dcontour`.

## [0.16.0] - 2017-01-11
### Updated
- Upgraded Plotly.js, the underlying library behind the `dash_core_components.Graph` component, to version 1.32.0 [#143](https://github.com/plotly/dash-core-components/pull/143). [Feature release 1.32.0](https://github.com/plotly/plotly.js/releases/tag/v1.32.0) includes:
  - Localization machinery, including an official German translation (locale `de`)
  - A new `violin` trace type
  - Selection improvements: `selected` and `unselected` attribute containers to customize selection states, Support for multi-selections, persistent selections.
  - `colorway` attribute to customize the trace-to-trace color sequence
  - Add `tickformatstops` to set tick format per cartesian axis range
  - And many more features and bug fixes

## [0.15.5] - 2017-01-08
### Fixed
- The `dash_core_components.Location` and `dash_core_components.Link` properties
should now work on Internet Explorer.
Thanks to @nedned for suggesting a solution.
Fixes https://github.com/plotly/dash-core-components/pull/113

## [0.15.4] - 2017-12-21
### Changed
- The `dash_core_components.Location` component now supports `hash`,
`href`, and `search` in addition to the already supported `pathname`
(mimicking the `window.location` API). `href` can be used to handle
`pathname`, `hash`, and `search` in aggregate, or each can be manipulated
independently.
- The `children` property of `dash_core_components.Markdown` and
`dash_core_components.SyntaxHighlighter` now accepts an
array of strings (previously it *had* to be a string). Now,
if an array is provided, it is collapsed into a string with line
breaks (see #134).

## [0.15.3] - 2017-12-11
### Fixed
- Patched plotly.js to version 1.31.2 [#125](https://github.com/plotly/dash-core-components/pull/125), including patch releases [1.31.2](https://github.com/plotly/plotly.js/releases/tag/v1.31.2) and [1.31.1](https://github.com/plotly/plotly.js/releases/tag/v1.31.1) with numerous bug fixes.


## [0.15.2] - 2017-11-24
### :sweat_smile: Added
- The `Interval` component has a new property: `n_intervals`. This is an
integer that increases every time that the interval passes. This allows you
to use the `Interval` component without using the `events=[Event(...)]` pattern
inside the callback.

This is similar to the `n_clicks` property of the `dash_html_components`
components.
This was the last use case for `events=[Event(...)]` inside the
`dash_core_components` library. Ultimately, we may be able to deprecate this
pattern.

### Changed
- The `dash_core_components.Input(type='number')` component actually converts
the values to floats or integers, instead of passing the numbers back as strings.
https://github.com/plotly/dash-core-components/pull/100
Big thanks to community contributor @Madhu94!

### Fixed
- The `disable_click` property in the `dcc.Upload` component now works.
https://github.com/plotly/dash-core-components/pull/106.
Big thanks to community contributor @Akronix!
- Several properties in several components had the wrong `propTypes`.
This has been fixed, improving the documentation for the Dash python classes
(and removing warnings in JS development).
Big thanks to community contributor @Akronix!

## [0.15.1] - 2017-11-23
### Fixed
- Attempt to fix the JS builds from 0.15.0 but actually nothing changed.

## [0.15.0] - 2017-11-19
- Bad build. See 0.15.2 for the correct build

## [0.14.0] - 2017-10-17
### :sparkles: Added
- An `Upload` component! :tada: See [https://plotly.com/dash/dash-core-components/upload](https://plotly.com/dash/dash-core-components/upload) for docs.

## [0.13.0] - 2017-10-05
### Updated
- Upgraded plotly.js to version 1.31.0. This includes:
  - Two huge feature releases by the plotly.js team! :clap: - [1.31.0](https://github.com/plotly/plotly.js/releases/tag/v1.31.0) and [1.30.0](https://github.com/plotly/plotly.js/releases/tag/v1.30.0), which contain:
    - A new `table` trace type
    - `geo.center` making geo views fully reproducible
    - Extend lasso and select-box drag modes to `bar`, `histogram`, `scattergeo`, and `choropleth` trace types
    - `aggregate` transforms
    - And many other features and bug fixes
  - Patch release [1.30.1](https://github.com/plotly/plotly.js/releases/tag/v1.30.1) with bug fixes

## [0.12.7] - 2017-09-26
### :bug: Fixed
- Fixed issues related to updating the `max_date_allowed` property of `DatePickerSingle` and `DatePickerRange`  programmatically through callbacks
- Clicking on the end date in the `DatePickerRange` will now open up the calendar to the end date (https://github.com/plotly/dash-core-components/issues/80)

### Maintenance
- Cleaned up `DatePickerSingle` and `DatePickerRange`

## [0.12.6] - 2017-09-11
### :bug: Fixed
-  Non-ascii characters, like chinese characters, are now supported as
   search strings in the `dcc.Dropdown` component (https://github.com/plotly/dash-core-components/pull/75)

## [0.12.5] - 2017-09-11
### :bug: Fixed
-  The `Interval` component was constantly resetting its interval on every update. Initially reported in https://community.plotly.com/t/multiple-interval-object-in-a-single-page/5699/3
- Removed the used `label` property from the `Slider` component
- Provide a more descriptive documentation for the `marks` property of the `Slider` component

### :stars: Added
- A `disabled` property on the `Interval` component will disable the interval component from firing its updates.

## [0.12.4] - 2017-08-18
### Added
- Added `className` and `style` properties to the parent `div`s of the `Checklist`, `Dropdown`, `Graph` and `RadioItems` component. As requested in https://github.com/plotly/dash-core-components/issues/57, solved in https://github.com/plotly/dash-core-components/pull/60

## [0.12.3] - 2017-08-17
### Fixed
- Previously, the `max_date_allowed` could not be selected. This issue has been fixed, issue first reported in https://community.plotly.com/t/solved-datepicker-in-dash/4816/10

## [0.12.2] - 2017-08-10
### Fixed
- Previously, when the `options` of a `dcc.Dropdown` would change, the options would no longer be searchable. That has been fixed. Issue was originally reported in https://community.plotly.com/t/dropdown-not-searching-values-when-typing/5323/3

## [0.12.1] - 2017-08-09
### Fixed
- Disabled portal settings on `dcc.DatePickerSingle` and `dcc.DatePickerRange` when `vertical=True`. `with_portal` and `with_full_screen_portal` will only apply if `vertical=False`.

## [0.12.0] - 2017-08-09
### Added
- Added two new date picker components: `dcc.DatePickerSingle` and `dcc.DatePickerRange`

## [0.11.1] - 2017-08-07
### Fixed
- Added support for all of the valid HTML attributes of the `Input` component.
- Added support for a few more `type` values of the `Input` component. The
  full list of valid types are 'text', 'number', 'password', 'email', 'range', 'search', 'tel', 'url', 'hidden'.
  Note that type values that don't have cross-browser support are not included (such as `datetime`)

## [0.11.0] - 2017-08-04
### Added
- The `Dropdown` component renders `options` much, much faster. It can render 50,000 options (client-side) without crashing! This fixes https://github.com/plotly/dash/issues/103

## [0.10.0] - 2017-08-03
### Updated
- Upgraded plotly.js to version 1.29.3, including feature releases [1.29.0](https://github.com/plotly/plotly.js/releases/tag/v1.29.0) and [1.28.0](https://github.com/plotly/plotly.js/releases/tag/v1.28.0), and patch releases [1.29.3](https://github.com/plotly/plotly.js/releases/tag/v1.29.3), [1.29.2](https://github.com/plotly/plotly.js/releases/tag/v1.29.2), [1.29.1](https://github.com/plotly/plotly.js/releases/tag/v1.29.1), [1.28.2](https://github.com/plotly/plotly.js/releases/tag/v1.28.2), [1.28.1](https://github.com/plotly/plotly.js/releases/tag/v1.28.1), and [1.27.1](https://github.com/plotly/plotly.js/releases/tag/v1.27.1) This includes TONS of fixes and improvements, notably:
    - Add touch interactions to cartesian, gl2d and ternary subplots including for
    select and lasso drag modes
    - Add support for contour line labels in contour and contourcarpet traces
    - Add support for select and lasso drag modes on scattermapbox traces
    - Add reset view and toggle hover mode bar buttons to mapbox subplots
    - Add support for array marker.opacity settings in scattermapbox traces
    - Add namelength layout and trace attribute to control the trace name's
    visible length in hover labels
    - Add cliponaxis attribute to scatter and scatterternary traces to allow
    markers and text nodes to be displayed above their subplot's axes
    - Add axis layer attribute with 'above traces' and 'below traces' values

## [0.9.0] - 2017-07-28
### Added
- A `config` property of the `Graph` component that exposes the [plotly.js config properties](https://plotly.com/javascript/configuration-options/). Here's an example that hides 2 buttons and makes the elements in the graph "editable":
```
import dash
import dash_core_components as dcc
import dash_html_components as html

app = dash.Dash()

app.layout = html.Div([
    dcc.Graph(
        id='my-graph',
        figure={'data': [{'x': [1, 2, 3]}]},
        config={'editable': True, 'modeBarButtonsToRemove': ['pan2d', 'lasso2d']}
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
```

## [0.8.0] - 2017-07-27
### Added
- A new `Textarea` component for displaying the simple Textarea HTML element. The content of the `Textarea` is controlled through the `value` property:
```
dcc.Textarea(id='my-text-area' value='''
SELECT * FROM MY_TABLES
LIMIT 10;
''')
```

## [0.7.1] - 2017-07-24
### Fixed
- Clearing a Graph selection box sets the `selectedData` value to `None` (`null` in JavaScript). Before, it didn't change the `selectedData` property, preventing the user and the Dash developer from clearing selections. Fixes https://github.com/plotly/dash/issues/97, thanks to @pmbaumgartner for reporting.


## [0.7.0] - 2017-07-20
### Added
- The `clearable` property to the `Dropdown`, which toggles on and off the "x" on the side of the dropdown that clears the current selection.
- The `searchable` property to the `Dropdown`, which toggles on and off whether the `Dropdown` is searchable.

### Fixed
- Clicking on the little `x` on the side of the Dropdown to clear the currently selected value didn't work. Now it does. If `multi=false`, then `null` (or Python's `None`) is set. If `multi=True`, then `[]` is set.

## [0.6.0] - 2017-07-18
### Added
- The `Slider` and the `RangeSlider` component can update when the user finishes dragging the slider rather than just while they drag. The default behaviour has remained the same (updates while dragging) but you can toggle that the updates only get fired on "mouse up" by setting `updatemode` to `'mouseup'` (`'drag'` is the default).
- A `Link` and `Location` were added. `Location` represents the address bar of the web browser and `Link` provides a way to modify the address bar without refreshing the page. Combined, these two components can be used to create a "single page app" with multiple URLs. That is, apps that have multiple URLs but surfing between the different pages doesn't trigger a full page refresh like it would with traditional links.
- Previously, if callback functions weren't supplied to a component, it wouldn't update. This caused a lot of confusion: users would create a simple layout without any callbacks and then wonder why the sliders wouldn't slide or the text inputs wouldn't update. Now, all of the components manage their own state and their appearance will update regardless of whether Dash has assigned a callback to them.

## [0.5.3] - 2017-07-03
### Added
- A `range` object is now included in the `selectedData` object that specifies
  that dimensions of the selected region.
- A `lassoPoints` object is now included in the `selectedData` object that
  provides coordinates of the lassoed region.

## [0.5.2] - 2017-07-03
### Added
- A new property `clear_on_unhover` on the `Graph` component will clear the
  `hoverData` property when the user "unhovers" from a point if True. If False,
  then the `hoverData` property will be equal to the data from the last point
  that was hovered over. The default is False.
