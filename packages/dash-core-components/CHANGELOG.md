# Change Log for dash-core-components
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

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
