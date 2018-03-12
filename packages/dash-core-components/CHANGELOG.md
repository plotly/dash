# Change Log for dash-core-components
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

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
