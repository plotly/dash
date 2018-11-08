# Change Log for dash-core-components
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

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
- Updated plotly.js to 1.42.1 [#354](https://github.com/plotly/dash-core-components/pull/354)
  - https://github.com/plotly/plotly.js/releases/tag/v1.42.0
  - https://github.com/plotly/plotly.js/releases/tag/v1.42.1
  - https://github.com/plotly/plotly.js/releases/tag/v1.42.2

### Fixed
- Fix runaway loops for `scattergl` lines and fill traces
  (bug introduced in 1.42.0) [#3199]
- Fix size and alignment in vertical modebars [#3193]
- Fix legend item rendering for traces with typed array marker
  settings [#3192]


### As part of [plotly.js 1.42.1](https://github.com/plotly/plotly.js/releases/tag/v1.42.1)

#### Fixed
- Fix IE regression introduced in 1.42.0 [#3187]
- Fix parcats text-shadowing on dark plot_bgcolor [#3191]
- Fix scatter3d text alignment [#3180]
- Fix hoverinfo flags in attribute descriptions [#3158]
- No longer list and coerce unused hoverlabel attribute in parcoods [#3158]
- No longer list and coerce transforms attributes in traces that don't support them [#3158]

### As part of [plotly.js 1.42.0](https://github.com/plotly/plotly.js/releases/tag/v1.42.0)

### Added
- Add `parcats` (aka parallel categories) trace type [#2963, #3072]
- Add new gl3d tick and title auto-rotation algorithm that limits text
  overlaps [#3084, #3104, #3131]
- Add support for reversed-range axes on gl3d subplots [#3141]
- Add modebar layout style attributes: `orientation`, `bgcolor`, `color`
  and `activecolor` [#3068, #3091]
- Add `title`, `titleposition` and `titlefont` attributes to `pie` traces [#2987]
- Add `hoverlabel.split` attribute to `ohlc` and `candlestick` traces to split
  hover labels into multiple pieces [#2959]
- Add support for `line.shape` values 'hv', 'vh', 'hvh' and 'vhv'
  in `scattergl` traces [#3087]
- Add handler for `PlotlyConfig.MathJaxConfig: 'local'` to override our default
  MathJax behavior which modifies the global MathJax config on load [#2994]
- Add support for graph div as first argument for `Plotly.makeTemplate`
  and `Plotly.validateTemplate` [#3111, #3118]
- Implement trace, node and link hoverinfo for `sankey` traces [#3096, #3150]
- Implement per-sector textfont settings in `pie` traces [#3130]

### Changed
- Use new Plotly logo in "Produced with Plotly" modebar button [#3068]
- Improve `histogram` autobin algorithm: allow partial bin specification,
  deprecate `autobin(x|y)` attributes, force stacked/grouped histograms to match size
  and have compatible `start` value [#3044]
- Count distinct values for category and date axis auto-type, which
  improves the detection of "NaN" string values in numerical data [#3070]
- Improve bar and pie textfont color inheritance [#3130]
- Improve `splom` first-render, axis range relayout and marker restyle
  performance [#3057, #3161]
- Make `splom` `xaxes` and `yaxes` list always have same length as the trace
  `dimensions` regardless of their partial visiblities [#3057]
- Improve axis `overlaying` documentation [#3082]

### Fixed
- Fix `gl3d` subplots on tablets [#3088]
- Fix responsive behavior under flexbox and grid CSS [#3056, #3090, #3122]
- Fix relayout calls turning back `autosize` on [#3120]
- Fix MathJax rendering (for recent versions of MathJax) [#2994]
- Fix `scattergl` update on graphs with fractional computed dimensions [#3132]
- Fix `scattergl` symbols in MS Edge [#2750]
- Fix `scattergl` selections on overlaying axes [#3067]
- Fix `scattergl` `tozero` fills with bad values [#3087, #3168]
- Fix `scattergl` fill layer ordering [#3087]
- Fix `scattergl` lines on reversed-range axes [#3078]
- Fix axis auto-type routine for boolean data [#3070]
- Fix `splom` axis placement when the diagonal is missing [#3057]
- Fix line `restyle` calls on `parcoords` traces [#3178]
- Fix `parcoods` rendering after `hovermode` relayout calls [#3123]
- Fix WebGL warnings for `scatter3d` traces with blank text items [#3171, #3177]
- Fix WebGL warnings for `scatter3d` trace with empty lines [#3174]
- Fix rendering of `scatter3d` lines for certain scene angles [#3163]
- Fix handling of large pad values in `sankey` traces [#3143]
- Fix `scatterpolargl`  to `scatterpolar` toggling [#3098]
- Fix `scatterpolargl` axis-autorange padding [#3098]
- Fix `bar` text position for traces with set `base` [#3156]
- Fix `bar` support for typed arrays for `width` and `offset` attributes [#3169]
- Fix aggregate transforms with bad group values [#3093]
- Fix transforms operating on auto-invisible traces [#3139]
- Fix templating for polar and carpet axes [#3092, #3095]
- Ignore invalid trace indices in restyle and update [#3114]
- Fix grid style `relayout` calls on graph with large `splom` traces [#3067]
- Fix logging on some old browsers [#3137]
- Remove erroneous warning `WARN: unrecognized full object value` when
  relayouting array containers [#3053]

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
### Added

- Upgraded Plotly.js, the underlying library behind the dash_core_components.Graph component, to version 1.41.3. See https://github.com/plotly/plotly.js/releases/tag/v1.41.3 for the official notes. 
Many of these features were funded directly by companies that rely on this library. If your organization or company would like to sponsor particular features or bug fixes in these open source libraries, please reach out: http://plot.ly/products/consulting-and-oem

### Fixed
As part of plotly.js release:

- Fix handling of hover `text` in `barpolar` traces [#3040]
- Fix `scatterpolar[gl]` `text` placement in hover label [#3040]
- Fix `pie` trace support for individual stroke width values [#3030]
- Fix handling of CSS `max-width` and `max-height` in auto-size routine [#3033]
- Rotate hover labels when `hovermode: 'y'` and a single trace produces multiple
  labels [#3043]
- Rotate hover labels when `hovermode: 'closest'` and multiple labels are
  generated including one from an horizontal trace [#3043]
- Fix hover label coloring on white bgcolor [#3048]
- Do not coerce nor validate `polar?.bar*` attributes on
  subplots w/o visible `barpolar` traces [#3023]
- Fix legacy polar attribute descriptions [#3023]

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
### Added

- Upgraded Plotly.js, the underlying library behind the dash_core_components.Graph component, to version 1.41.0. See https://github.com/plotly/plotly.js/releases/tag/v1.41.0 for the official notes. 
Many of these features were funded directly by companies that rely on this library. If your organization or company would like to sponsor particular features or bug fixes in these open source libraries, please reach out: http://plot.ly/products/consulting-and-oem

As part of plotly.js release:

- Enable selection by clicking on points via new layout attribute `clickmode`
  and flag `'select'` [#2944]
- Add stacked area charts via new attributes `stackgroup` and `stackgaps` in
  `scatter` traces [#2960]
- Add `barpolar` traces - which replace and augment `area` traces [#2954]
- Add `polar.hole` to punch hole at the middle of polar subplot offsetting the
  start of the radial range [#2977, #2996]
- Add an 'inner' radial axis drag box on polar subplots [#2977]
- Add `{responsive: true}` plot config option [#2974]
- Emit `plotly_webglcontextlost` event on WebGL context lost [#2986]
- Support all numbered HTML entities (decimal and hex) in text elements [#2932]
- Add Welsh (`cy`) locale [#2945]

### Changed
As part of plotly.js release:

- Attribute meta information is now stripped be stripped out of bundles (made
  with bundlers that support browserify transforms) by default [#1584]
- Draw polar axis ticks above polar axis lines [#2977]
- Improve ordering of trace hover labels for matching positions [#2960]
- Speed polar subplot radial drag interactions [#2954]
- Improve pseudo-html conversion performance [#2932]
- Bump `regl-splom` requirement to `^1.0.4` [#2956]
- Bump `glslify` requirement to `^6.3.1` [#2990]
- Use `gl-text` instead of `@etpinard/gl-text` [#2956]

### Fixed
As part of plotly.js release:

- Fix `scatter` ordering in inner SVG `<g>` on some restyle calls [#2978]
- Fix cartesian axis autorange edge cases [#2960]
- Fix double-decoding of some HTML entities in text nodes [#2927]
- Fix `scattergl` line traces rendered after non-line traces [#2990]
- Fix legend positioning on graphs with very large margins [#2983]
- Fix rendering of ternary subplots fix with `showticklabels: false` [#2993]
- Fix show/hide updates of tick and tick labels on ternary subplots [#2993]
- Fix handling of multi-selections in ternary subplots [#2944]
- Fix `sankey` hover under `hovermode: false` [#2949]
- Fix `sankey` positioning for non-default `domain.x` values [#2984]
- Fix `type: 'date'` polar radial axes [#2954]
- Fix send-to-cloud modebar buttons on graphs with typed arrays [#2995]
- Fix handling of custom transforms that make their own data arrays in
  `Plotly.react`[#2973]
- Fix missing violin and colorbar attributes in `gd._fullData` [#2850]

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
- Upgraded Plotly.js, the underlying library behind the
`dash_core_components.Graph` component, to [version 1.40.1](https://github.com/plotly/plotly.js/releases/tag/v1.40.1).
See https://github.com/plotly/plotly.js/releases/tag/v1.40.1 for the official notes.

As part of plotly.js release:
### Changed
- Bump `browserify` to `v16` [#2923]
- Bump `glslify` to `v6.2.1` [#2923]
- Use `color-normlize@1.3.0` throughout code base [#2923]
### Fixed
- Fix logic for hiding zero lines when they conflict with axis lines [#2936]
- Fix `exponentformat` values `'e'` and `'E'` on log axes [#2921]
- Fix dynamic layer ordering of heatmap and carpet traces [#2917]
- Fix `Plotly.downloadImage` when using graph id or figure object
as first argument [#2931]
- Fix regl-based rendering when WebGL buffer dimensions don't match canvas
dimensions [#2939]

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
adding support for IDE autocomplete ect.

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
### Added
- Upgraded Plotly.js, the underlying library behind the
`dash_core_components.Graph` component, to [version 1.39.1](https://github.com/plotly/plotly.js/releases/tag/v1.39.1).
See https://github.com/plotly/plotly.js/releases/tag/v1.39.1 for the official notes.

    Many of these features were funded directly by companies that rely on this library.
    If your organization or company would like to sponsor particular features or
    bug fixes in these open source libraries, please reach out: http://plot.ly/products/consulting-and-oem

As part of plotly.js release:
- Add support for on-graph text in scattergl traces [#2737](https://github.com/plotly/plotly.js/pull/2737), [#2783](https://github.com/plotly/plotly.js/pull/2783)
- Add gridshape attribute to polar subplots with values 'circular' (the default) and 'linear' (to draw polygon grids) [#2739](https://github.com/plotly/plotly.js/pull/2739)
- Add support for colorbar linked to marker.color values for splom,
scatterpolar and scatterpolargl traces [#2681](https://github.com/plotly/plotly.js/pull/2681)
- Revamp icon settings in custom mode bar buttons, allowing users to specify their own dimensions and SVG transforms [#2762](https://github.com/plotly/plotly.js/pull/2762)
- Add plotlyServerURL config option [#2760](https://github.com/plotly/plotly.js/pull/2760)
- Added no-WebGL warnings for graphs with scattergl, scatterpolargl, splom and parcoords traces [#2697](https://github.com/plotly/plotly.js/pull/2697)

### Fixed
As part of plotly.js release:
- Fix Plotly.react's handling of changing auto-margins [#2681](https://github.com/plotly/plotly.js/pull/2681)
- Make plotting/updating WebGL-based traces fail gracefully when WebGL isn't
supported [#2697](https://github.com/plotly/plotly.js/pull/2697)
- Fix mapbox layout layer updates [#2734](https://github.com/plotly/plotly.js/pull/2734)
- Fix mapbox event inconsistencies [#2766](https://github.com/plotly/plotly.js/pull/2766)
- Correctly emit plotly_relayout at end of scroll on mapbox subplots [#2709](https://github.com/plotly/plotly.js/pull/2709)
- Fix scatter3d scalar hovertext handling [#2698](https://github.com/plotly/plotly.js/pull/2698)
- Fix line decimation for segments crossing the viewport [#2705](https://github.com/plotly/plotly.js/pull/2705)
- Fix surface trace contours when first level has length zero [#2712](https://github.com/plotly/plotly.js/pull/2712)
- Fix contour(x|y|z).highlight partial settings [#2712](https://github.com/plotly/plotly.js/pull/2712)
- Fix old date timezone precision in Chrome 67+ [#2747](https://github.com/plotly/plotly.js/pull/2747)
- Fix x-only zoom moves when xaxis.fixedrange: true[#2776](https://github.com/plotly/plotly.js/pull/2776)
- Fix colorbar edits for parcoords and histogram traces [#2681](https://github.com/plotly/plotly.js/pull/2681)
- Fix bandwidth for single-value violins [#2775](https://github.com/plotly/plotly.js/pull/2775)
- Make Plots.resize work when layout attribute is gone from graph div [#2710](https://github.com/plotly/plotly.js/pull/2710)
- Fix colorscale attribute descriptions [#2658](https://github.com/plotly/plotly.js/pull/2658)    

## [0.23.0]
### Added
- Upgraded Plotly.js, the underlying library behind the
`dash_core_components.Graph` component, to [version 1.38.0](https://github.com/plotly/plotly.js/releases/tag/v1.38.0).
See https://github.com/plotly/plotly.js/releases/tag/v1.38.0 for the official notes.

    - Add 3D `cone` traces to visualize vector fields [#2641](https://github.com/plotly/plotly.js/pull/2641), [#2647](https://github.com/plotly/plotly.js/pull/2647)
    - Add ability to interactively change length and rotate line shapes [#2594](https://github.com/plotly/plotly.js/pull/2594)
    - Add `toImageButtonOptions` config object to override to-image mode bar button options [#2607](https://github.com/plotly/plotly.js/pull/2607)
    - Add `plotly_legendclick` and `plotly_legenddoubleclick` events [#2581](https://github.com/plotly/plotly.js/pull/2581)
    - Add splom (aka scatter plot matrix) traces [#2505](https://github.com/plotly/plotly.js/pull/2505)
    - Add selection and improve legend items for ohlc and candlestick [#2561](https://github.com/plotly/plotly.js/pull/2561)

### Changed
As part of the Plotly.js upgrade:
- Improve cartesian scroll and pan (mostly) performance for graphs with
many marker or/and text nodes [#2623](https://github.com/plotly/plotly.js/pull/2623)
- Improve multi-axis axis-range relayout performance by updating minimal set of
axes instead of all axes [#2628](https://github.com/plotly/plotly.js/pull/2628)
- New and improved point-clustering algorithm for `scattergl` [#2499](https://github.com/plotly/plotly.js/pull/2499)

### Fixed
As part of the plotly.js upgrade:
- Fix `scattergl` error bar computations when input value are numeric strings [#2620](https://github.com/plotly/plotly.js/pull/2620)
- Fix `scattergl` error bar computations for `x0`/`dx` and `y0`/`dy` coordinates [#2620](https://github.com/plotly/plotly.js/pull/2620)
- Fix `violin` kde span edge cases [#2650](https://github.com/plotly/plotly.js/pull/2650)
- Make `sankey` traces accept numeric strings [#2629](https://github.com/plotly/plotly.js/pull/2629)
- Fix axis range edits under axis constraints [#2620](https://github.com/plotly/plotly.js/pull/2620)
- Fix "sloppy click" event emission during cartesian zoom [#2649](https://github.com/plotly/plotly.js/pull/2649)
- Fix layout `grid` validation which lead to exceptions [#2638](https://github.com/plotly/plotly.js/pull/2638)
- Fix `parcoords` rendering in old Safari version [#2612](https://github.com/plotly/plotly.js/pull/2612)
- Link to https://get.webgl.org instead of http version in no WebGL message [#2617](https://github.com/plotly/plotly.js/pull/2617)

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
### Added
- Upgraded Plotly.js, the underlying library behind the
`dash_core_components.Graph` component, to [version 1.35.2](https://github.com/plotly/plotly.js/releases/tag/v1.34.0).
See https://github.com/plotly/plotly.js/releases/tag/v1.35.2 for the official notes.

    Many of these features were funded directly by companies that rely on this library.
    If your organization or company would like to sponsor particular features or
    bug fixes in these open source libraries, please reach out: http://plot.ly/products/consulting-and-oem

    - Add `automargin` attribute to cartesian axes which auto-expands margins
      when ticks, tick labels and/or axis titles do not fit on the graph [#2243](https://github.com/plotly/plotly.js/pull/2243)
    - Add support for typed arrays as data array inputs [#2388](https://github.com/plotly/plotly.js/pull/2388)
    - Add layout `grids` attribute for easy subplot generation [#2399](https://github.com/plotly/plotly.js/pull/2399)
    - Implement `cliponaxis: false` for bar text [#2378](https://github.com/plotly/plotly.js/pull/2378)
    - Add opposite axis attributes for range slider to control y axis range behavior [#2364](https://github.com/plotly/plotly.js/pull/2364)
    - Generalize `hoverdistance` and `spikedistance` for area-like objects [#2379](https://github.com/plotly/plotly.js/pull/2379)
    - Bring `scattergl` auto-range logic to par with SVG `scatter` [#2404](https://github.com/plotly/plotly.js/pull/2404)
    - Add selected/unselected marker color size support to `scattermapbox` traces [#2361](https://github.com/plotly/plotly.js/pull/2361)

### Changed
As part of the Plotly.js upgrade:
- Bump `mapbox-gl` to `v0.44.0` [#2361](https://github.com/plotly/plotly.js/pull/2361)
- Bump `glslify` to `v6.1.1` [#2377](https://github.com/plotly/plotly.js/pull/2377)
- Stop relinking `customdata`, `ids` and any matching objects
  in `gd._fullLayout` during `Plots.supplyDefaults` [#2375](https://github.com/plotly/plotly.js/pull/2375)

### Fixed
As part of the plotly.js upgrade:
- Fix buggy auto-range / auto-margin interaction
  leading to axis range inconsistencies on redraws
  (this bug was mostly noticeable on graphs with legends) [#2437](https://github.com/plotly/plotly.js/pull/2437)
- Bring back `scattergl` lines under select/lasso `dragmode`
  (bug introduced in `1.33.0`) [#2377](https://github.com/plotly/plotly.js/pull/2377)
- Fix `scattergl` visible toggling for graphs with multiple traces
  with different modes (bug introduced in `1.33.0`) [#2442](https://github.com/plotly/plotly.js/pull/2442)
- Bring back `spikelines` for traces other than `scatter`
  (bug introduced in `1.33.0`) [#2379](https://github.com/plotly/plotly.js/pull/2379)
- Fix `Plotly.Fx.hover` acting on multiple subplots
  (bug introduced in `1.32.0`) [#2379](https://github.com/plotly/plotly.js/pull/2379)
- Fix range slider with stacked y axes positioning
  (bug introduced in `1.32.0`) [#2451](https://github.com/plotly/plotly.js/pull/2451)
- Fix `scattergl` color clustering [#2377](https://github.com/plotly/plotly.js/pull/2377)
- Fix `Plotly.restyle` for `scattergl` `fill` [#2377](https://github.com/plotly/plotly.js/pull/2377)
- Fix multi-line y-axis label positioning [#2424](https://github.com/plotly/plotly.js/pull/2424)
- Fix centered hover labels edge cases [#2440, #2445](https://github.com/plotly/plotly.js/pull/2440)
- Fix hover labels in bar groups in compare mode [#2414](https://github.com/plotly/plotly.js/pull/2414)
- Fix axes and axis lines removal [#2416](https://github.com/plotly/plotly.js/pull/2416)
- Fix auto-sizing in `Plotly.react` [#2437](https://github.com/plotly/plotly.js/pull/2437)
- Fix error bars for `Plotly.react` and uneven data arrays [#2360](https://github.com/plotly/plotly.js/pull/2360)
- Fix edits for date-string referenced annotations [#2368](https://github.com/plotly/plotly.js/pull/2368)
- Fix `z` hover labels with exponents [#2422](https://github.com/plotly/plotly.js/pull/2422)
- Fix yet another histogram edge case [#2413](https://github.com/plotly/plotly.js/pull/2413)
- Fix fall back for contour labels when there's only one contour [#2411](https://github.com/plotly/plotly.js/pull/2411)
- Fix `scatterpolar` category angular period calculations [#2449](https://github.com/plotly/plotly.js/pull/2449)
- Clear select outlines on mapbox zoomstart [#2361](https://github.com/plotly/plotly.js/pull/2361)
- Fix legend click to causes legend scroll bug [#2426](https://github.com/plotly/plotly.js/pull/2426)

## [0.20.2] - 2018-03-05
### Fixed
- The `selectedData`, `clickData`, and `hoverData` callbacks were being attached without being
removed every time the graph was updated. They are now removed and reattached. #172

## [0.20.1] - 2018-03-01
### Fixed
- The `serve_locally` was broken - the Plotly.js bundle wasn't being served correctly.

## [0.20.0] - 2018-03-01
### Added
- Upgraded Plotly.js, the underlying library behind the
`dash_core_components.Graph` component, to [version 1.34.0](https://github.com/plotly/plotly.js/releases/tag/v1.34.0).
See https://github.com/plotly/plotly.js/releases/tag/v1.34.0 for the official notes.

    Many of these features were funded directly by companies that rely on this library.
    If your organization or company would like to sponsor particular features or
    bug fixes in these open source libraries, please reach out: http://plot.ly/products/consulting-and-oem

    - Add constraint-type contours to `contour` traces [https://github.com/plotly/plotly.js/pull/2270]
    - Add `notched` and `notchwidth` attributes to `box` traces [https://github.com/plotly/plotly.js/pull/2305]
    - Add localization machinery to auto-formatted date axis ticks [https://github.com/plotly/plotly.js/pull/2261]
    - Add support for `text` in `mesh3d` traces [https://github.com/plotly/plotly.js/pull/2327]
    - Add support for scalar `text` in `surface` traces [https://github.com/plotly/plotly.js/pull/2327]
    - Make mode bar for graphs with multiple subplot types more usable [https://github.com/plotly/plotly.js/pull/2339]

### Fixed
- The `Graph` component now uses `Plotly.react` instead of `Plotly.newPlot`. This should fix issues when repeatedly updating GL chart types (`surface`, `scatter3d`, `scattergl`). #170
    - Many other bug fixes from the PLotly.js upgrade, including:
    - Prevent page scroll on mobile device on `gl2d` and `gl3d` subplots [https://github.com/plotly/plotly.js/pull/2296]
    - Fix multi-marker `scattergl` selection errors (bug introduced in `1.33.0`) [https://github.com/plotly/plotly.js/pull/2295]
    - Fix trace `opacity` restyle for `scattergl` traces (bug introduced in `1.33.0`) [https://github.com/plotly/plotly.js/pull/2299]
    - Fix `scattergl` handling of `selectedpoints` across multiple traces [https://github.com/plotly/plotly.js/pull/2311]
    - Fix `scattergl` horizontal and vertical line rendering [https://github.com/plotly/plotly.js/pull/2340]
    - Fix `table` when content-less cells and headers are supplied [https://github.com/plotly/plotly.js/pull/2314]
    - Fix `hoverformat` on `visible: false` cartesian axes (bug introduced in `1.33.0`) [https://github.com/plotly/plotly.js/pull/2329]
    - Fix handling of double negative translate transform values [https://github.com/plotly/plotly.js/pull/2339]
    - Fix compare `hovermode` fallback for non-cartesian subplot types [https://github.com/plotly/plotly.js/pull/2339]


## [0.19.0] - 2018-02-11
### Changed
- `PropTypes` now uses `prop-types` package instead of `React` to support move to React 16+

## [0.18.1] - 2017-01-25
### Fixed
- Upgraded Plotly.js, the underlying library behind the
`dash_core_components.Graph` component, to [version 1.33.1](https://github.com/plotly/plotly.js/releases/tag/v1.33.1). Fixes include
    - Fix selection on scattergl plots with >20k points [#2266](https://github.com/plotly/plotly.js/issues/2266)
    - Update Spanish localization with new strings [#2268](https://github.com/plotly/plotly.js/issues/2268)
    - Fix test_dashboard overly rigid restriction so parcoods works there [#2273](https://github.com/plotly/plotly.js/issues/2273)
    - Make layout.colorway compatible with sankey traces [#2277](https://github.com/plotly/plotly.js/issues/2277)
    - Fix click events on fixedrange subplots [#2279](https://github.com/plotly/plotly.js/issues/2279)
    - Remove ghost fill when trace data is emptied out [#2280](https://github.com/plotly/plotly.js/issues/2280)
    - Fix resizing of new scattergl plots [#2283](https://github.com/plotly/plotly.js/issues/2283)
    - Fix positioning of carpet axis titles for cheaterslope edge cases [#2285](https://github.com/plotly/plotly.js/issues/2285)
    - Fix coloring and hover info for heatmaps and contour maps with nonuniform bins [#2288](https://github.com/plotly/plotly.js/issues/2288)


## [0.18.0] - 2017-01-19
### Added
- Upgraded Plotly.js, the underlying library behind the
`dash_core_components.Graph` component, to [version 1.33.0](https://github.com/plotly/plotly.js/releases/tag/v1.33.0).
This was a huge release! Here are some of the new features that
are available. See https://github.com/plotly/plotly.js/releases/tag/v1.33.0 for the official notes.

    Many of these features were funded directly by companies that rely on this library.
    If your organization or company would like to sponsor particular features or
    bug fixes in these open source libraries, please reach out: http://plot.ly/products/consulting-and-oem

    - Completely rewritten `scattergl` trace type using `regl` [plotly.js/pull/2258](https://github.com/plotly/plotly.js/pull/2258)
    - Completely rewritten polar chart renderer accompanied by new
      `scatterpolar` and `scatterpolargl` trace types [plotly.js/pull/2200](https://github.com/plotly/plotly.js/pull/2200)
    - Add the ability to draw layout images and layout shapes on subplot
      with `scattergl` traces [plotly.js/pull/2258](https://github.com/plotly/plotly.js/pull/2258)
    - Add `fill` capabilities to `scattergl` traces [plotly.js/pull/2258](https://github.com/plotly/plotly.js/pull/2258)
    - Add `spikedistance`, `hoverdistance` and `skipsnap` for more customizable
      spikes and hover behavior on cartesian subplots [plotly.js/pull/2247](https://github.com/plotly/plotly.js/pull/2247)
    - Add official Spanish translation (locale `es`) [plotly.js/pull/2249](https://github.com/plotly/plotly.js/pull/2249)
    - Add official French translation (locale `fr`) [plotly.js/pull/2252](https://github.com/plotly/plotly.js/pull/2252)


### Changed
- With the plotly.js upgrade, the old polar trace types
  (`scatter` with `(r, t)` coordinates, bar with (`(r, t)` coordinates and
   `area`) are now deprecated).

### Fixed
- Several bugs with the `dcc.Graph` component were fixed with the plotly.js upgrade.
These include:
    - Fix `gl2d` tick label on pan interaction regression [plotly.js/pull/2258](https://github.com/plotly/plotly.js/pull/2258)
    - Fix `candlestick` hover label regression (bug introduced in v1.32.0) [plotly.js/pull/2264](https://github.com/plotly/plotly.js/pull/2264)
    - Fix several `gl2d` axis related bugs with new regl-based `scattergl` [plotly.js/pull/2258](https://github.com/plotly/plotly.js/pull/2258)
      See full list under the On-par gl2d milestone https://github.com/plotly/plotly.js/milestone/3
    - Fix several polar bugs with `scatterpolar` [plotly.js/pull/2200].(https://github.com/plotly/plotly.js/pull/2200)
      See full list under the On-par polar milestone https://github.com/plotly/plotly.js/milestone/2
    - Fix `scattergl` marker.colorscale handling [plotly.js/pull/2258](https://github.com/plotly/plotly.js/pull/2258)
    - Fix decimal and thousands settings in `de` locale [plotly.js/pull/2246](https://github.com/plotly/plotly.js/pull/2246)
    - Make scroll handler _passive_, removing those annoying console warnings [plotly.js/pull/2251](https://github.com/plotly/plotly.js/pull/2251)

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
### Added
- Upgraded Plotly.js, the underlying library behind the
`dash_core_components.Graph` component, to [version 1.32.0](https://github.com/plotly/plotly.js/releases/tag/v1.32.0).
This was a huge release! Here are some of the new features that
are available. See https://github.com/plotly/plotly.js/releases/tag/v1.32.0 for the official notes.
- Add localization machinery  [https://github.com/plotly/plotly.js/pull/2195, https://github.com/plotly/plotly.js/pull/2207, https://github.com/plotly/plotly.js/pull/2210, https://github.com/plotly/plotly.js/pull/2232],
   including an official German translation (locale `de`) [https://github.com/plotly/plotly.js/pull/2217]
- Add `violin` trace type [https://github.com/plotly/plotly.js/pull/2116]
- Add `selected` and `unselected` attribute containers to customize selection states [https://github.com/plotly/plotly.js/pull/2135]
- Add support for multi-selections [https://github.com/plotly/plotly.js/pull/2140]
- Add layout `colorway` to custom the trace-to-trace color sequence [https://github.com/plotly/plotly.js/pull/2156]
- Add `tickformatstops` to set tick format per cartesian axis range [https://github.com/plotly/plotly.js/pull/1965]
- Add hover labels and selections to box points [https://github.com/plotly/plotly.js/pull/2094]
- Histogram events & bin hover label improvements [https://github.com/plotly/plotly.js/pull/2113]
- Add support for aggregation in `pie` traces [https://github.com/plotly/plotly.js/pull/2117]
- Add annotations `startarrowhead`, `arrowside`, `startarrowsize` and `startstandoff` attributes [https://github.com/plotly/plotly.js/pull/2164]
- Add `zhoverformat` to format `z` values in `heatmap`, `contour` and 2d histogram traces [https://github.com/plotly/plotly.js/pull/2106, https://github.com/plotly/plotly.js/pull/2127]
- Add `marker.opacity` to bar traces [https://github.com/plotly/plotly.js/pull/2163]
- Add `Cividis` colorscale [https://github.com/plotly/plotly.js/pull/2178]
- Implement transform inverse mapping [https://github.com/plotly/plotly.js/pull/2126, https://github.com/plotly/plotly.js/pull/2162]
- Selections are now persistent [https://github.com/plotly/plotly.js/pull/2135]
- Rename _Save and edit plot in cloud_ mode bar button _Edit in Chart Studio_ [https://github.com/plotly/plotly.js/pull/2183]

### Fixed
Here the bug fixes in the `Graph` component brought to you by the plotly.js release.
See https://github.com/plotly/plotly.js/releases/tag/v1.32.0 for the official notes.

- Fix right-click handling [https://github.com/plotly/plotly.js/pull/2241]
- Miscellaneous fixes for `table` traces [https://github.com/plotly/plotly.js/pull/2107, https://github.com/plotly/plotly.js/pull/2182]
- Fix horizontal legend items alignment edge case [https://github.com/plotly/plotly.js/pull/2149]
- Fix shape and updatemenu layering [https://github.com/plotly/plotly.js/pull/2121]
- Fix bar with error bar with set `ids` edge case [https://github.com/plotly/plotly.js/pull/2169]
- Fix `cliponaxis: false` for non linear cartesian axes [https://github.com/plotly/plotly.js/pull/2177]
- Fix heatmap non-uniform brick gaps problem [https://github.com/plotly/plotly.js/pull/2213]
- Fix choropleth selection when `visible: false` trace are present on graph [https://github.com/plotly/plotly.js/pull/2099, https://github.com/plotly/plotly.js/pull/2109]
- Fix yet another contour drawing bug [https://github.com/plotly/plotly.js/pull/2091]
- Clean up pie event data [https://github.com/plotly/plotly.js/pull/2117]
- Fix scatter + bar hover edge cases [https://github.com/plotly/plotly.js/pull/2218]
- Allow hover labels to extend to edges of graph area [https://github.com/plotly/plotly.js/pull/2215]
- Harden location-to-feature against non-string country names for geo subplot [https://github.com/plotly/plotly.js/pull/2122]
- Remove obsolete `smith` attribute from plot schema [https://github.com/plotly/plotly.js/pull/2093]
- Fix colorbar class name [https://github.com/plotly/plotly.js/pull/2139]



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
- Upgrade the version of [plotly.js](https://github.com/plotly/plotly.js) from 1.31.0 to 1.31.2. See the list of fixes here: https://github.com/plotly/plotly.js/blob/master/CHANGELOG.md


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
- An `Upload` component! :tada: See [https://plot.ly/dash/dash-core-components/upload](https://plot.ly/dash/dash-core-components/upload) for docs.

## [0.13.0] - 2017-10-05
### Added
- Bumped [plotly.js](https://github.com/plotly/plotly.js) from `v1.29.3` to `v1.30.0`.
This was a huge release by the plotly.js team! :clap:
See the full changelog here: https://github.com/plotly/plotly.js/releases/tag/v1.31.0.
The following improvements from this version update apply to dash:
    - Add `table` trace type [2030](https://github.com/plotly/plotly.js/issue/2030)
    - Add `geo.center` making geo views fully reproducible using layout attributes [2030](https://github.com/plotly/plotly.js/issue/2030)
    - Add lasso and select-box drag modes to `scattergeo` and `choropleth` traces [2030](https://github.com/plotly/plotly.js/issue/2030)
    - Add lasso and select-box drag modes to `bar` and `histogram` traces [2045](https://github.com/plotly/plotly.js/issue/2045)
    - Throttle lasso and select-box events for smoother behavior [2040](https://github.com/plotly/plotly.js/issue/2040)
    - Add constraintext attribute for bar traces [1931](https://github.com/plotly/plotly.js/1931)
    - Add axis layer attribute to ternary axes [1952](https://github.com/plotly/plotly.js/1952)
    - Add cross-trace matching auto-binning logic to histogram traces [1944](https://github.com/plotly/plotly.js/1944)
    - Harmonize gl3d and gl2d zoom speed with cartesian behavior [2041](https://github.com/plotly/plotly.js/issue/2041)
    - Fix handling of extreme off-plot data points in scatter lines [2060](https://github.com/plotly/plotly.js/issue/2060)
    - Fix `hoverinfo` array support for `scattergeo`, `choropleth`, `scatterternary` and `scattermapbox` traces [2055](https://github.com/plotly/plotly.js/issue/2055)
    - Fix single-bin histogram edge case [2028](https://github.com/plotly/plotly.js/issue/2028)
    - Fix autorange for bar with base zero [2050](https://github.com/plotly/plotly.js/issue/2050)
    - Fix annotations arrow rendering when graph div is off the DOM [2046](https://github.com/plotly/plotly.js/issue/2046)
    - Fix hover for graphs with `scattergeo` markers outside 'usa' scope [2030](https://github.com/plotly/plotly.js/issue/2030)
    - Fix handling of cross anti-meridian geo `lonaxis` ranges [2030](https://github.com/plotly/plotly.js/issue/2030)
    - Fix miter limit for lines on geo subplots [2030](https://github.com/plotly/plotly.js/issue/2030)
    - Fix `marker.opacity` handling for `scattergeo` bubbles [2030](https://github.com/plotly/plotly.js/issue/2030)
    - Fix layout animation of secondary axes [1999](https://github.com/plotly/plotly.js/issue/1999)
    - Fix `sankey` hover text placement for empty `link.label` items [2016](https://github.com/plotly/plotly.js/issue/2016)
    - Fix `sankey` rendering of nodes with very small values [2017](https://github.com/plotly/plotly.js/issue/2017,2021] https://github.com/plotly/plotly.js/issue/2021)
    - Fix `sankey` hover label positioning on pages that style the 'svg-container' div node [2027](https://github.com/plotly/plotly.js/issue/2027)
    - Fix hover label exponents [1932](https://github.com/plotly/plotly.js/issue/1932)
    - Fix scatter fill with isolated endpoints [1933](https://github.com/plotly/plotly.js/issue/1933)
    - Fix parcoords axis tick scale when ticktext is unordered [1945](https://github.com/plotly/plotly.js/issue/1945)
    - Fix sankey with 4 multi-links or more [1934](https://github.com/plotly/plotly.js/issue/1934)
    - Fix exponent labels beyond SI prefixes [1930](https://github.com/plotly/plotly.js/issue/1930)
    - Fix image generation for marker gradient legend items [1928](https://github.com/plotly/plotly.js/issue/1928)
    - Fix parcoords image generation when multiple parcoords graphs are present on page [1947](https://github.com/plotly/plotly.js/issue/1947)
    - Ignore bare closing tags in pseudo-html string inputs [1926](https://github.com/plotly/plotly.js/issue/1926)


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
-  The `Interval` component was constantly resetting its interval on every update. Initially reported in https://community.plot.ly/t/multiple-interval-object-in-a-single-page/5699/3
- Removed the used `label` property from the `Slider` component
- Provide a more descriptive documentation for the `marks` property of the `Slider` component

### :stars: Added
- A `disabled` property on the `Interval` component will disable the interval component from firing its updates.

## [0.12.4] - 2017-08-18
### Added
- Added `className` and `style` properties to the parent `div`s of the `Checklist`, `Dropdown`, `Graph` and `RadioItems` component. As requested in https://github.com/plotly/dash-core-components/issues/57, solved in https://github.com/plotly/dash-core-components/pull/60

## [0.12.3] - 2017-08-17
### Fixed
- Previously, the `max_date_allowed` could not be selected. This issue has been fixed, issue first reported in https://community.plot.ly/t/solved-datepicker-in-dash/4816/10

## [0.12.2] - 2017-08-10
### Fixed
- Previously, when the `options` of a `dcc.Dropdown` would change, the options would no longer be searchable. That has been fixed. Issue was originally reported in https://community.plot.ly/t/dropdown-not-searching-values-when-typing/5323/3

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
### Added
- Upgrade [plotly.js](https://github.com/plotly/plotly.js) (the library behind the `Graph` component) from 1.27.0 to 1.29.3. This includes TONS of fixes and improvements, see https://github.com/plotly/plotly.js/releases for more details. Notable improvements include:
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

    And fixes include:
    - Fix axis line width, length, and positioning for coupled subplots
    - Fix alignment of cartesian tick labels
    - Fix rendering and updates of overlaying axis lines
    - Fix hover for 2D traces with custom colorbar tickvals
    - Fix hover and event data for heatmapgl and contourgl traces
    - Fix event data for pie and sankey traces
    - Fix drag mode 'pan' in IE and Edge
    - Fix bar, error bar and box point scaling on scroll zoom
    - Fix shading issue in surface trace in iOS
    - Fix lasso and select drag modes for `scatterternary` traces
    - Fix cases of intersecting contour lines on log axes
    - Fix animation of annotations, shapes and images
    - Fix histogram bin computation when more than 5000 bins are needed
    - Fix tick label rendering when more than 1000 labels are present

## [0.9.0] - 2017-07-28
### Added
- A `config` property of the `Graph` component that exposes the [plotly.js config properties](https://plot.ly/javascript/configuration-options/). Here's an example that hides 2 buttons and makes the elements in the graph "editable":
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
- A `Link` and `Location` were added. `Location` represents the address bar of the web browser and `Link` provides a way to modify the address bar without refreshing the page. Combined, these two components can be used to create a "single page app" with multiple URLs. That is, apps that have mulitple URLs but surfing between the different pages doesn't trigger a full page refresh like it would with traditional links.
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
