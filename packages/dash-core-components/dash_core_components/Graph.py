# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Graph(Component):
    """A Graph component.


Keyword arguments:
- id (string; optional): The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.
- clickData (dict; optional): Data from latest click event. Read-only.
- clickAnnotationData (dict; optional): Data from latest click annotation event. Read-only.
- hoverData (dict; optional): Data from latest hover event. Read-only.
- clear_on_unhover (boolean; optional): If True, `clear_on_unhover` will clear the `hoverData` property
when the user "unhovers" from a point.
If False, then the `hoverData` property will be equal to the
data from the last point that was hovered over.
- selectedData (dict; optional): Data from latest select event. Read-only.
- relayoutData (dict; optional): Data from latest relayout event which occurs
when the user zooms or pans on the plot or other
layout-level edits. Has the form `{<attr string>: <value>}`
describing the changes made. Read-only.
- restyleData (list; optional): Data from latest restyle event which occurs
when the user toggles a legend item, changes
parcoords selections, or other trace-level edits.
Has the form `[edits, indices]`, where `edits` is an object
`{<attr string>: <value>}` describing the changes made,
and `indices` is an array of trace indices that were edited.
Read-only.
- figure (dict; optional): Plotly `figure` object. See schema:
https://plot.ly/javascript/reference
Only supports `data` array and `layout` object.
`config` is set separately by the `config` property,
and `frames` is not supported.
- style (dict; optional): Generic style overrides on the plot div
- className (string; optional): className of the parent div
- animate (boolean; optional): Beta: If true, animate between updates using
plotly.js's `animate` function
- animation_options (dict; optional): Beta: Object containing animation settings.
Only applies if `animate` is `true`
- config (optional): Plotly.js config options.
See https://plot.ly/javascript/configuration-options/
for more info.. config has the following type: dict containing keys 'staticPlot', 'editable', 'edits', 'autosizable', 'queueLength', 'fillFrame', 'frameMargins', 'scrollZoom', 'doubleClick', 'showTips', 'showAxisDragHandles', 'showAxisRangeEntryBoxes', 'showLink', 'sendData', 'linkText', 'displayModeBar', 'modeBarButtonsToRemove', 'modeBarButtonsToAdd', 'modeBarButtons', 'displaylogo', 'plotGlPixelRatio', 'topojsonURL', 'mapboxAccessToken'.
Those keys have the following types:
  - staticPlot (boolean; optional): no interactivity, for export or image generation
  - editable (boolean; optional): we can edit titles, move annotations, etc - sets all pieces of `edits`
unless a separate `edits` config item overrides individual parts
  - edits (optional): a set of editable properties. edits has the following type: dict containing keys 'annotationPosition', 'annotationTail', 'annotationText', 'axisTitleText', 'colorbarPosition', 'colorbarTitleText', 'legendPosition', 'legendText', 'shapePosition', 'titleText'.
Those keys have the following types:
  - annotationPosition (boolean; optional): annotationPosition: the main anchor of the annotation, which is the
text (if no arrow) or the arrow (which drags the whole thing leaving
the arrow length & direction unchanged)
  - annotationTail (boolean; optional): just for annotations with arrows, change the length and direction of the arrow
  - annotationText (boolean; optional)
  - axisTitleText (boolean; optional)
  - colorbarPosition (boolean; optional)
  - colorbarTitleText (boolean; optional)
  - legendPosition (boolean; optional)
  - legendText (boolean; optional): edit the trace name fields from the legend
  - shapePosition (boolean; optional)
  - titleText (boolean; optional): the global `layout.title`
  - autosizable (boolean; optional): DO autosize once regardless of layout.autosize
(use default width or height values otherwise)
  - queueLength (number; optional): set the length of the undo/redo queue
  - fillFrame (boolean; optional): if we DO autosize, do we fill the container or the screen?
  - frameMargins (number; optional): if we DO autosize, set the frame margins in percents of plot size
  - scrollZoom (boolean; optional): mousewheel or two-finger scroll zooms the plot
  - doubleClick (a value equal to: false, 'reset', 'autosize', 'reset+autosize'; optional): double click interaction (false, 'reset', 'autosize' or 'reset+autosize')
  - showTips (boolean; optional): new users see some hints about interactivity
  - showAxisDragHandles (boolean; optional): enable axis pan/zoom drag handles
  - showAxisRangeEntryBoxes (boolean; optional): enable direct range entry at the pan/zoom drag points
(drag handles must be enabled above)
  - showLink (boolean; optional): link to open this plot in plotly
  - sendData (boolean; optional): if we show a link, does it contain data or just link to a plotly file?
  - linkText (string; optional): text appearing in the sendData link
  - displayModeBar (a value equal to: true, false, 'hover'; optional): display the mode bar (true, false, or 'hover')
  - modeBarButtonsToRemove (list; optional): remove mode bar button by name.
All modebar button names at https://github.com/plotly/plotly.js/blob/master/src/components/modebar/buttons.js
Common names include:
 - sendDataToCloud
- (2D): zoom2d, pan2d, select2d, lasso2d, zoomIn2d, zoomOut2d, autoScale2d, resetScale2d
- (Cartesian): hoverClosestCartesian, hoverCompareCartesian
- (3D): zoom3d, pan3d, orbitRotation, tableRotation, handleDrag3d, resetCameraDefault3d, resetCameraLastSave3d, hoverClosest3d
- (Geo): zoomInGeo, zoomOutGeo, resetGeo, hoverClosestGeo
- hoverClosestGl2d, hoverClosestPie, toggleHover, resetViews
  - modeBarButtonsToAdd (list; optional): add mode bar button using config objects
  - modeBarButtons (boolean | number | string | dict | list; optional): fully custom mode bar buttons as nested array,
where the outer arrays represents button groups, and
the inner arrays have buttons config objects or names of default buttons
  - displaylogo (boolean; optional): add the plotly logo on the end of the mode bar
  - plotGlPixelRatio (number; optional): increase the pixel ratio for Gl plot images
  - topojsonURL (string; optional): URL to topojson files used in geo charts
  - mapboxAccessToken (boolean | number | string | dict | list; optional): Mapbox access token (required to plot mapbox trace types)
If using an Mapbox Atlas server, set this option to '',
so that plotly.js won't attempt to authenticate to the public Mapbox server.
- loading_state (optional): Object that holds the loading state object coming from dash-renderer. loading_state has the following type: dict containing keys 'is_loading', 'prop_name', 'component_name'.
Those keys have the following types:
  - is_loading (boolean; optional): Determines if the component is loading or not
  - prop_name (string; optional): Holds which property is loading
  - component_name (string; optional): Holds the name of the component that is loading"""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, clickData=Component.UNDEFINED, clickAnnotationData=Component.UNDEFINED, hoverData=Component.UNDEFINED, clear_on_unhover=Component.UNDEFINED, selectedData=Component.UNDEFINED, relayoutData=Component.UNDEFINED, restyleData=Component.UNDEFINED, figure=Component.UNDEFINED, style=Component.UNDEFINED, className=Component.UNDEFINED, animate=Component.UNDEFINED, animation_options=Component.UNDEFINED, config=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'clickData', 'clickAnnotationData', 'hoverData', 'clear_on_unhover', 'selectedData', 'relayoutData', 'restyleData', 'figure', 'style', 'className', 'animate', 'animation_options', 'config', 'loading_state']
        self._type = 'Graph'
        self._namespace = 'dash_core_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'clickData', 'clickAnnotationData', 'hoverData', 'clear_on_unhover', 'selectedData', 'relayoutData', 'restyleData', 'figure', 'style', 'className', 'animate', 'animation_options', 'config', 'loading_state']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Graph, self).__init__(**args)
