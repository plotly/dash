# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Graph(Component):
    """A Graph component.


Keyword arguments:
- id (string; optional): The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.
- clickData (dict; optional): Data from latest click event
- clickAnnotationData (dict; optional): Data from latest click annotation event
- hoverData (dict; optional): Data from latest hover event
- clear_on_unhover (boolean; optional): If True, `clear_on_unhover` will clear the `hoverData` property
when the user "unhovers" from a point.
If False, then the `hoverData` property will be equal to the
data from the last point that was hovered over.
- selectedData (dict; optional): Data from latest select event
- relayoutData (dict; optional): Data from latest relayout event which occurs
when the user zooms or pans on the plot
- figure (dict; optional): Plotly `figure` object. See schema:
https://plot.ly/javascript/reference
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

Available events: 'click', 'clickannotation', 'hover', 'selected', 'relayout', 'unhover'"""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, clickData=Component.UNDEFINED, clickAnnotationData=Component.UNDEFINED, hoverData=Component.UNDEFINED, clear_on_unhover=Component.UNDEFINED, selectedData=Component.UNDEFINED, relayoutData=Component.UNDEFINED, figure=Component.UNDEFINED, style=Component.UNDEFINED, className=Component.UNDEFINED, animate=Component.UNDEFINED, animation_options=Component.UNDEFINED, config=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'clickData', 'clickAnnotationData', 'hoverData', 'clear_on_unhover', 'selectedData', 'relayoutData', 'figure', 'style', 'className', 'animate', 'animation_options', 'config']
        self._type = 'Graph'
        self._namespace = 'dash_core_components'
        self._valid_wildcard_attributes =            []
        self.available_events = ['click', 'clickannotation', 'hover', 'selected', 'relayout', 'unhover']
        self.available_properties = ['id', 'clickData', 'clickAnnotationData', 'hoverData', 'clear_on_unhover', 'selectedData', 'relayoutData', 'figure', 'style', 'className', 'animate', 'animation_options', 'config']
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

    def __repr__(self):
        if(any(getattr(self, c, None) is not None
               for c in self._prop_names
               if c is not self._prop_names[0])
           or any(getattr(self, c, None) is not None
                  for c in self.__dict__.keys()
                  if any(c.startswith(wc_attr)
                  for wc_attr in self._valid_wildcard_attributes))):
            props_string = ', '.join([c+'='+repr(getattr(self, c, None))
                                      for c in self._prop_names
                                      if getattr(self, c, None) is not None])
            wilds_string = ', '.join([c+'='+repr(getattr(self, c, None))
                                      for c in self.__dict__.keys()
                                      if any([c.startswith(wc_attr)
                                      for wc_attr in
                                      self._valid_wildcard_attributes])])
            return ('Graph(' + props_string +
                   (', ' + wilds_string if wilds_string != '' else '') + ')')
        else:
            return (
                'Graph(' +
                repr(getattr(self, self._prop_names[0], None)) + ')')
