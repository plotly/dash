# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
import numbers  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal  # noqa: F401
from dash.development.base_component import Component, _explicitize_args

try:
    from dash.development.base_component import ComponentType  # noqa: F401
except ImportError:
    ComponentType = typing.TypeVar("ComponentType", bound=Component)


from plotly.graph_objects import Figure


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

        - staticPlot (boolean; optional):
            No interactivity, for export or image generation.

        - plotlyServerURL (string; optional):
            Base URL for a Plotly cloud instance, if `showSendToCloud` is
            enabled.

        - editable (boolean; optional):
            We can edit titles, move annotations, etc - sets all pieces of
            `edits` unless a separate `edits` config item overrides
            individual parts.

        - editSelection (boolean; optional):
            Enables moving selections.

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

        - autosizable (boolean; optional):
            DO autosize once regardless of layout.autosize (use default
            width or height values otherwise).

        - responsive (boolean; optional):
            Whether to change layout size when the window size changes.

        - queueLength (number; optional):
            Set the length of the undo/redo queue.

        - fillFrame (boolean; optional):
            If we DO autosize, do we fill the container or the screen?.

        - frameMargins (number; optional):
            If we DO autosize, set the frame margins in percents of plot
            size.

        - scrollZoom (boolean; optional):
            Mousewheel or two-finger scroll zooms the plot.

        - doubleClick (a value equal to: false, 'reset', 'autosize', 'reset+autosize'; optional):
            Double click interaction (False, 'reset', 'autosize' or
            'reset+autosize').

        - doubleClickDelay (number; optional):
            Delay for registering a double-click event in ms. The minimum
            value is 100 and the maximum value is 1000. By default this is
            300.

        - showTips (boolean; optional):
            New users see some hints about interactivity.

        - showAxisDragHandles (boolean; optional):
            Enable axis pan/zoom drag handles.

        - showAxisRangeEntryBoxes (boolean; optional):
            Enable direct range entry at the pan/zoom drag points (drag
            handles must be enabled above).

        - showLink (boolean; optional):
            Link to open this plot in plotly.

        - sendData (boolean; optional):
            If we show a link, does it contain data or just link to a
            plotly file?.

        - linkText (string; optional):
            Text appearing in the sendData link.

        - displayModeBar (a value equal to: true, false, 'hover'; optional):
            Display the mode bar (True, False, or 'hover').

        - showSendToCloud (boolean; optional):
            Should we include a modebar button to send this data to a
            Plotly Cloud instance, linked by `plotlyServerURL`. By default
            this is False.

        - showEditInChartStudio (boolean; optional):
            Should we show a modebar button to send this data to a Plotly
            Chart Studio plot. If both this and showSendToCloud are
            selected, only showEditInChartStudio will be honored. By
            default this is False.

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

        - modeBarButtonsToAdd (list; optional):
            Add mode bar button using config objects.

        - modeBarButtons (boolean | number | string | dict | list; optional):
            Fully custom mode bar buttons as nested array, where the outer
            arrays represents button groups, and the inner arrays have
            buttons config objects or names of default buttons.

        - toImageButtonOptions (dict; optional):
            Modifications to how the toImage modebar button works.

            `toImageButtonOptions` is a dict with keys:

            - format (a value equal to: 'jpeg', 'png', 'webp', 'svg'; optional):
                The file format to create.

            - filename (string; optional):
                The name given to the downloaded file.

            - width (number; optional):
                Width of the downloaded file, in px.

            - height (number; optional):
                Height of the downloaded file, in px.

            - scale (number; optional):
                Extra resolution to give the file after rendering it with
                the given width and height.

        - displaylogo (boolean; optional):
            Add the plotly logo on the end of the mode bar.

        - watermark (boolean; optional):
            Add the plotly logo even with no modebar.

        - plotGlPixelRatio (number; optional):
            Increase the pixel ratio for Gl plot images.

        - topojsonURL (string; optional):
            URL to topojson files used in geo charts.

        - mapboxAccessToken (boolean | number | string | dict | list; optional):
            Mapbox access token (required to plot mapbox trace types) If
            using an Mapbox Atlas server, set this option to '', so that
            plotly.js won't attempt to authenticate to the public Mapbox
            server.

        - locale (string; optional):
            The locale to use. Locales may be provided with the plot
            (`locales` below) or by loading them on the page, see:
            https://github.com/plotly/plotly.js/blob/master/dist/README.md#to-include-localization.

        - locales (dict; optional):
            Localization definitions, if you choose to provide them with
            the plot rather than registering them globally.

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

        - layout (dict; optional)

        - frames (list of dicts; optional)

    - hoverData (dict; optional):
        Data from latest hover event. Read-only.

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
        Data from latest select event. Read-only."""

    _children_props = []
    _base_nodes = ["children"]
    _namespace = "dash_core_components"
    _type = "Graph"
    ConfigEdits = TypedDict(
        "ConfigEdits",
        {
            "annotationPosition": NotRequired[bool],
            "annotationTail": NotRequired[bool],
            "annotationText": NotRequired[bool],
            "axisTitleText": NotRequired[bool],
            "colorbarPosition": NotRequired[bool],
            "colorbarTitleText": NotRequired[bool],
            "legendPosition": NotRequired[bool],
            "legendText": NotRequired[bool],
            "shapePosition": NotRequired[bool],
            "titleText": NotRequired[bool],
        },
    )

    ConfigToImageButtonOptions = TypedDict(
        "ConfigToImageButtonOptions",
        {
            "format": NotRequired[Literal["jpeg", "png", "webp", "svg"]],
            "filename": NotRequired[str],
            "width": NotRequired[typing.Union[int, float, numbers.Number]],
            "height": NotRequired[typing.Union[int, float, numbers.Number]],
            "scale": NotRequired[typing.Union[int, float, numbers.Number]],
        },
    )

    Config = TypedDict(
        "Config",
        {
            "staticPlot": NotRequired[bool],
            "plotlyServerURL": NotRequired[str],
            "editable": NotRequired[bool],
            "editSelection": NotRequired[bool],
            "edits": NotRequired["ConfigEdits"],
            "autosizable": NotRequired[bool],
            "responsive": NotRequired[bool],
            "queueLength": NotRequired[typing.Union[int, float, numbers.Number]],
            "fillFrame": NotRequired[bool],
            "frameMargins": NotRequired[typing.Union[int, float, numbers.Number]],
            "scrollZoom": NotRequired[bool],
            "doubleClick": NotRequired[
                Literal[False, "reset", "autosize", "reset+autosize"]
            ],
            "doubleClickDelay": NotRequired[typing.Union[int, float, numbers.Number]],
            "showTips": NotRequired[bool],
            "showAxisDragHandles": NotRequired[bool],
            "showAxisRangeEntryBoxes": NotRequired[bool],
            "showLink": NotRequired[bool],
            "sendData": NotRequired[bool],
            "linkText": NotRequired[str],
            "displayModeBar": NotRequired[Literal[True, False, "hover"]],
            "showSendToCloud": NotRequired[bool],
            "showEditInChartStudio": NotRequired[bool],
            "modeBarButtonsToRemove": NotRequired[typing.Sequence],
            "modeBarButtonsToAdd": NotRequired[typing.Sequence],
            "modeBarButtons": NotRequired[typing.Any],
            "toImageButtonOptions": NotRequired["ConfigToImageButtonOptions"],
            "displaylogo": NotRequired[bool],
            "watermark": NotRequired[bool],
            "plotGlPixelRatio": NotRequired[typing.Union[int, float, numbers.Number]],
            "topojsonURL": NotRequired[str],
            "mapboxAccessToken": NotRequired[typing.Any],
            "locale": NotRequired[str],
            "locales": NotRequired[dict],
        },
    )

    @_explicitize_args
    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        responsive: typing.Optional[Literal[True, False, "auto"]] = None,
        clickData: typing.Optional[dict] = None,
        clickAnnotationData: typing.Optional[dict] = None,
        hoverData: typing.Optional[dict] = None,
        clear_on_unhover: typing.Optional[bool] = None,
        selectedData: typing.Optional[dict] = None,
        relayoutData: typing.Optional[dict] = None,
        extendData: typing.Optional[typing.Union[typing.Sequence, dict]] = None,
        prependData: typing.Optional[typing.Union[typing.Sequence, dict]] = None,
        restyleData: typing.Optional[typing.Sequence] = None,
        figure: typing.Optional[typing.Union[Figure, dict]] = None,
        style: typing.Optional[typing.Any] = None,
        className: typing.Optional[str] = None,
        mathjax: typing.Optional[bool] = None,
        animate: typing.Optional[bool] = None,
        animation_options: typing.Optional[dict] = None,
        config: typing.Optional["Config"] = None,
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
