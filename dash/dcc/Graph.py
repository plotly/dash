# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Graph(Component):
    """A Graph component.
    Graph can be used to render any plotly.js-powered data visualization.

    You can define callbacks based on user interaction with Graphs such as
    hovering, clicking or selecting

    Keyword arguments:

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - animate (boolean; default False):
        Beta: If True, animate between updates using plotly.js's `animate`
        function.

    - animation_options (dict; default {    frame: {        redraw: False,    },    transition: {        duration: 750,        ease: 'cubic-in-out',    },}):
        Beta: Object containing animation settings. Only applies if
        `animate` is `True`.

    - className (string; optional):
        className of the parent div.

    - clear_on_unhover (boolean; default False):
        If True, `clear_on_unhover` will clear the `hoverData` property
        when the user \"unhovers\" from a point. If False, then the
        `hoverData` property will be equal to the data from the last point
        that was hovered over.

    - clickAnnotationData (dict; optional):
        Data from latest click annotation event. Read-only.

    - clickData (dict; optional):
        Data from latest click event. Read-only.

    - config (dict; optional):
        Plotly.js config options. See
        https://plotly.com/javascript/configuration-options/ for more
        info.

        `config` is a dict with keys:

        - autosizable (boolean; optional):
            DO autosize once regardless of layout.autosize (use default
            width or height values otherwise).

        - displayModeBar (a value equal to: true, false, 'hover'; optional):
            Display the mode bar (True, False, or 'hover').

        - displaylogo (boolean; optional):
            Add the plotly logo on the end of the mode bar.

        - doubleClick (a value equal to: false, 'reset', 'autosize', 'reset+autosize'; optional):
            Double click interaction (False, 'reset', 'autosize' or
            'reset+autosize').

        - doubleClickDelay (number; optional):
            Delay for registering a double-click event in ms. The minimum
            value is 100 and the maximum value is 1000. By default this is
            300.

        - editSelection (boolean; optional):
            Enables moving selections.

        - editable (boolean; optional):
            We can edit titles, move annotations, etc - sets all pieces of
            `edits` unless a separate `edits` config item overrides
            individual parts.

        - edits (dict; optional):
            A set of editable properties.

            `edits` is a dict with keys:

            - annotationPosition (boolean; optional):
                The main anchor of the annotation, which is the text (if
                no arrow) or the arrow (which drags the whole thing
                leaving the arrow length & direction unchanged).

            - annotationTail (boolean; optional):
                Just for annotations with arrows, change the length and
                direction of the arrow.

            - annotationText (boolean; optional)

            - axisTitleText (boolean; optional)

            - colorbarPosition (boolean; optional)

            - colorbarTitleText (boolean; optional)

            - legendPosition (boolean; optional)

            - legendText (boolean; optional):
                Edit the trace name fields from the legend.

            - shapePosition (boolean; optional)

            - titleText (boolean; optional):
                The global `layout.title`.

        - fillFrame (boolean; optional):
            If we DO autosize, do we fill the container or the screen?.

        - frameMargins (number; optional):
            If we DO autosize, set the frame margins in percents of plot
            size.

        - linkText (string; optional):
            Text appearing in the sendData link.

        - locale (string; optional):
            The locale to use. Locales may be provided with the plot
            (`locales` below) or by loading them on the page, see:
            https://github.com/plotly/plotly.js/blob/master/dist/README.md#to-include-localization.

        - locales (dict; optional):
            Localization definitions, if you choose to provide them with
            the plot rather than registering them globally.

        - mapboxAccessToken (boolean | number | string | dict | list; optional):
            Mapbox access token (required to plot mapbox trace types) If
            using an Mapbox Atlas server, set this option to '', so that
            plotly.js won't attempt to authenticate to the public Mapbox
            server.

        - modeBarButtons (boolean | number | string | dict | list; optional):
            Fully custom mode bar buttons as nested array, where the outer
            arrays represents button groups, and the inner arrays have
            buttons config objects or names of default buttons.

        - modeBarButtonsToAdd (list; optional):
            Add mode bar button using config objects.

        - modeBarButtonsToRemove (list; optional):
            Remove mode bar button by name. All modebar button names at
            https://github.com/plotly/plotly.js/blob/master/src/components/modebar/buttons.js
            Common names include: sendDataToCloud; (2D) zoom2d, pan2d,
            select2d, lasso2d, zoomIn2d, zoomOut2d, autoScale2d,
            resetScale2d; (Cartesian) hoverClosestCartesian,
            hoverCompareCartesian; (3D) zoom3d, pan3d, orbitRotation,
            tableRotation, handleDrag3d, resetCameraDefault3d,
            resetCameraLastSave3d, hoverClosest3d; (Geo) zoomInGeo,
            zoomOutGeo, resetGeo, hoverClosestGeo; hoverClosestGl2d,
            hoverClosestPie, toggleHover, resetViews.

        - plotGlPixelRatio (number; optional):
            Increase the pixel ratio for Gl plot images.

        - plotlyServerURL (string; optional):
            Base URL for a Plotly cloud instance, if `showSendToCloud` is
            enabled.

        - queueLength (number; optional):
            Set the length of the undo/redo queue.

        - responsive (boolean; optional):
            Whether to change layout size when the window size changes.

        - scrollZoom (boolean; optional):
            Mousewheel or two-finger scroll zooms the plot.

        - sendData (boolean; optional):
            If we show a link, does it contain data or just link to a
            plotly file?.

        - showAxisDragHandles (boolean; optional):
            Enable axis pan/zoom drag handles.

        - showAxisRangeEntryBoxes (boolean; optional):
            Enable direct range entry at the pan/zoom drag points (drag
            handles must be enabled above).

        - showEditInChartStudio (boolean; optional):
            Should we show a modebar button to send this data to a Plotly
            Chart Studio plot. If both this and showSendToCloud are
            selected, only showEditInChartStudio will be honored. By
            default this is False.

        - showLink (boolean; optional):
            Link to open this plot in plotly.

        - showSendToCloud (boolean; optional):
            Should we include a modebar button to send this data to a
            Plotly Cloud instance, linked by `plotlyServerURL`. By default
            this is False.

        - showTips (boolean; optional):
            New users see some hints about interactivity.

        - staticPlot (boolean; optional):
            No interactivity, for export or image generation.

        - toImageButtonOptions (dict; optional):
            Modifications to how the toImage modebar button works.

            `toImageButtonOptions` is a dict with keys:

            - filename (string; optional):
                The name given to the downloaded file.

            - format (a value equal to: 'jpeg', 'png', 'webp', 'svg'; optional):
                The file format to create.

            - height (number; optional):
                Height of the downloaded file, in px.

            - scale (number; optional):
                Extra resolution to give the file after rendering it with
                the given width and height.

            - width (number; optional):
                Width of the downloaded file, in px.

        - topojsonURL (string; optional):
            URL to topojson files used in geo charts.

        - watermark (boolean; optional):
            Add the plotly logo even with no modebar.

    - extendData (list | dict; optional):
        Data that should be appended to existing traces. Has the form
        `[updateData, traceIndices, maxPoints]`, where `updateData` is an
        object containing the data to extend, `traceIndices` (optional) is
        an array of trace indices that should be extended, and `maxPoints`
        (optional) is either an integer defining the maximum number of
        points allowed or an object with key:value pairs matching
        `updateData` Reference the Plotly.extendTraces API for full usage:
        https://plotly.com/javascript/plotlyjs-function-reference/#plotlyextendtraces.

    - figure (dict; default {    data: [],    layout: {},    frames: [],}):
        Plotly `figure` object. See schema:
        https://plotly.com/javascript/reference  `config` is set
        separately by the `config` property.

        `figure` is a dict with keys:

        - data (list of dicts; optional)

        - frames (list of dicts; optional)

        - layout (dict; optional)

    - hoverData (dict; optional):
        Data from latest hover event. Read-only.

    - loading_state (dict; optional):
        Object that holds the loading state object coming from
        dash-renderer.

        `loading_state` is a dict with keys:

        - component_name (string; optional):
            Holds the name of the component that is loading.

        - is_loading (boolean; optional):
            Determines if the component is loading or not.

        - prop_name (string; optional):
            Holds which property is loading.

    - mathjax (boolean; default False):
        If True, loads mathjax v3 (tex-svg) into the page and use it in
        the graph.

    - prependData (list | dict; optional):
        Data that should be prepended to existing traces. Has the form
        `[updateData, traceIndices, maxPoints]`, where `updateData` is an
        object containing the data to prepend, `traceIndices` (optional)
        is an array of trace indices that should be prepended, and
        `maxPoints` (optional) is either an integer defining the maximum
        number of points allowed or an object with key:value pairs
        matching `updateData` Reference the Plotly.prependTraces API for
        full usage:
        https://plotly.com/javascript/plotlyjs-function-reference/#plotlyprependtraces.

    - relayoutData (dict; optional):
        Data from latest relayout event which occurs when the user zooms
        or pans on the plot or other layout-level edits. Has the form
        `{<attr string>: <value>}` describing the changes made. Read-only.

    - responsive (a value equal to: true, false, 'auto'; default 'auto'):
        If True, the Plotly.js plot will be fully responsive to window
        resize and parent element resize event. This is achieved by
        overriding `config.responsive` to True, `figure.layout.autosize`
        to True and unsetting `figure.layout.height` and
        `figure.layout.width`. If False, the Plotly.js plot not be
        responsive to window resize and parent element resize event. This
        is achieved by overriding `config.responsive` to False and
        `figure.layout.autosize` to False. If 'auto' (default), the Graph
        will determine if the Plotly.js plot can be made fully responsive
        (True) or not (False) based on the values in `config.responsive`,
        `figure.layout.autosize`, `figure.layout.height`,
        `figure.layout.width`. This is the legacy behavior of the Graph
        component.  Needs to be combined with appropriate dimension /
        styling through the `style` prop to fully take effect.

    - restyleData (list; optional):
        Data from latest restyle event which occurs when the user toggles
        a legend item, changes parcoords selections, or other trace-level
        edits. Has the form `[edits, indices]`, where `edits` is an object
        `{<attr string>: <value>}` describing the changes made, and
        `indices` is an array of trace indices that were edited.
        Read-only.

    - selectedData (dict; optional):
        Data from latest select event. Read-only.

    - style (dict; optional):
        Generic style overrides on the plot div."""

    _children_props = []
    _base_nodes = ["children"]
    _namespace = "dash_core_components"
    _type = "Graph"

    @_explicitize_args
    def __init__(
        self,
        id=Component.UNDEFINED,
        responsive=Component.UNDEFINED,
        clickData=Component.UNDEFINED,
        clickAnnotationData=Component.UNDEFINED,
        hoverData=Component.UNDEFINED,
        clear_on_unhover=Component.UNDEFINED,
        selectedData=Component.UNDEFINED,
        relayoutData=Component.UNDEFINED,
        extendData=Component.UNDEFINED,
        prependData=Component.UNDEFINED,
        restyleData=Component.UNDEFINED,
        figure=Component.UNDEFINED,
        style=Component.UNDEFINED,
        className=Component.UNDEFINED,
        mathjax=Component.UNDEFINED,
        animate=Component.UNDEFINED,
        animation_options=Component.UNDEFINED,
        config=Component.UNDEFINED,
        loading_state=Component.UNDEFINED,
        **kwargs
    ):
        self._prop_names = [
            "id",
            "animate",
            "animation_options",
            "className",
            "clear_on_unhover",
            "clickAnnotationData",
            "clickData",
            "config",
            "extendData",
            "figure",
            "hoverData",
            "loading_state",
            "mathjax",
            "prependData",
            "relayoutData",
            "responsive",
            "restyleData",
            "selectedData",
            "style",
        ]
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "id",
            "animate",
            "animation_options",
            "className",
            "clear_on_unhover",
            "clickAnnotationData",
            "clickData",
            "config",
            "extendData",
            "figure",
            "hoverData",
            "loading_state",
            "mathjax",
            "prependData",
            "relayoutData",
            "responsive",
            "restyleData",
            "selectedData",
            "style",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Graph, self).__init__(**args)
