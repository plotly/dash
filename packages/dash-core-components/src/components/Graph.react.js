import React, {Component, PropTypes} from 'react';
import {contains, filter, has, isNil, type} from 'ramda';
/* global Plotly:true */

const filterEventData = (gd, eventData, event) => {
    let filteredEventData;
    if (contains(event, ['click', 'hover', 'selected'])) {
        const points = [];

        if (isNil(eventData)) {
            return null;
        }

        /*
         * remove `data`, `layout`, `xaxis`, etc
         * objects from the event data since they're so big
         * and cause JSON stringify ciricular structure errors.
         *
         * also, pull down the `customdata` point from the data array
         * into the event object
         */
        const data = gd.data;

        for(let i=0; i < eventData.points.length; i++) {
            const fullPoint = eventData.points[i];
            const pointData = filter(function(o) {
                return !contains(type(o), ['Object', 'Array'])
            }, fullPoint);
            if (has('curveNumber', fullPoint) &&
                has('pointNumber', fullPoint) &&
                has('customdata', data[pointData.curveNumber])
            ) {
                pointData['customdata'] = data[
                    pointData.curveNumber
                ].customdata[fullPoint.pointNumber];
            }

            // specific to histogram. see https://github.com/plotly/plotly.js/pull/2113/
            if (has('pointNumbers', fullPoint)) {
                pointData.pointNumbers = fullPoint.pointNumbers;
            }

            points[i] = pointData;

        }
        filteredEventData = {points}
    } else if (event === 'relayout') {
        /*
         * relayout shouldn't include any big objects
         * it will usually just contain the ranges of the axes like
         * "xaxis.range[0]": 0.7715822247381828,
         * "xaxis.range[1]": 3.0095292008680063`
         */
        filteredEventData = eventData;
    }
    if (has('range', eventData)) {
        filteredEventData.range = eventData.range;
    }
    if (has('lassoPoints', eventData)) {
        filteredEventData.lassoPoints = eventData.lassoPoints;
    }
    return filteredEventData;
};

export default class PlotlyGraph extends Component {
    constructor(props) {
        super(props);
        this.bindEvents = this.bindEvents.bind(this);
        this.state = {hasPlotted: false};
    }

    plot(props) {
        const {id, figure, animate, animation_options, config} = props;
        const {hasPlotted} = this.state;
        const gd = document.getElementById(id);
        if (animate && hasPlotted && figure.data.length === gd.data.length) {
            return Plotly.animate(id, figure, animation_options);
        } else {
            return  Plotly.newPlot(id, figure.data, figure.layout, config).then(() => {
                this.bindEvents(props);
                this.setState({hasPlotted: true});
            });
        }
    }

    bindEvents(props) {
        const {id, fireEvent, setProps, clear_on_unhover} = props;

        const gd = document.getElementById(id);

        gd.on('plotly_click', (eventData) => {
            const clickData = filterEventData(gd, eventData, 'click');
            if (!isNil(clickData)) {
                if (setProps) setProps({clickData});
                if (fireEvent) fireEvent({event: 'click'});
            }
        });
        gd.on('plotly_hover', (eventData) => {
            const hoverData = filterEventData(gd, eventData, 'hover');
            if (!isNil(hoverData)) {
                if (setProps) setProps({hoverData});
                if (fireEvent) fireEvent({event: 'hover'})
            }
        });
        gd.on('plotly_selected', (eventData) => {
            const selectedData = filterEventData(gd, eventData, 'selected');
            if (!isNil(selectedData)) {
                if (setProps) setProps({selectedData});
                if (fireEvent) fireEvent({event: 'selected'});
            }
        });
        gd.on('plotly_deselect', () => {
            if (setProps) setProps({selectedData: null});
            if (fireEvent) fireEvent({event: 'selected'});
        });
        gd.on('plotly_relayout', (eventData) => {
            const relayoutData = filterEventData(gd, eventData, 'relayout');
            if (!isNil(relayoutData)) {
                if (setProps) setProps({relayoutData});
                if (fireEvent) fireEvent({event: 'relayout'});
            }
        });
        gd.on('plotly_unhover', () => {
            if (clear_on_unhover) {
                if (setProps) setProps({hoverData: null});
                if (fireEvent) fireEvent({event: 'unhover'});
            }
        });
    }

    componentDidMount() {
        this.plot(this.props).then(() => {
            window.addEventListener('resize', () => {
                Plotly.Plots.resize(document.getElementById(this.props.id));
            });
        });
    }

    componentWillUnmount() {
        if (this.eventEmitter) {
            this.eventEmitter.removeAllListeners();
        }
    }

    shouldComponentUpdate(nextProps) {
        return (
            this.props.id !== nextProps.id ||
            JSON.stringify(this.props.style) !== JSON.stringify(nextProps.style)
        );
    }

    componentWillReceiveProps(nextProps) {
        const idChanged = this.props.id !== nextProps.id;
        if (idChanged) {
            /*
             * then the dom needs to get re-rendered with a new ID.
             * the graph will get updated in componentDidUpdate
             */
            return;
        }

        const figureChanged = this.props.figure !== nextProps.figure;

        /*
         * Rebind events in case fireEvent or setProps
         * wasn't defined on initial render
         * TODO - Is it safe to rebind events?
         */
        const shouldBindEvents = (
            (!this.props.setProps && nextProps.setProps) ||
            (!this.props.fireEvent && nextProps.fireEvent)
        );
        if (figureChanged) {
            this.plot(nextProps);
        } else if (shouldBindEvents) {
            this.bindEvents(nextProps);
        }
    }

    componentDidUpdate(prevProps) {
        if (prevProps.id !== this.props.id) {
            this.plot(this.props);
        }
    }

    render(){
        const {className, id, style} = this.props;

        return (
            <div
                key={id}
                id={id}
                style={style}
                className={className}
            />
        );

    }
}

PlotlyGraph.propTypes = {
    id: PropTypes.string.isRequired,
    /**
     * Data from latest click event
     */
    clickData: PropTypes.object,

    /**
     * Data from latest hover event
     */
    hoverData: PropTypes.object,

    /**
     * If True, `clear_on_unhover` will clear the `hoverData` property
     * when the user "unhovers" from a point.
     * If False, then the `hoverData` property will be equal to the
     * data from the last point that was hovered over.
     */
    clear_on_unhover: PropTypes.bool,

    /**
     * Data from latest select event
     */
    selectedData: PropTypes.object,

    /**
     * Data from latest relayout event which occurs
     * when the user zooms or pans on the plot
     */
    relayoutData: PropTypes.object,

    /**
     * Plotly `figure` object. See schema:
     * https://plot.ly/javascript/reference
     */
    figure: PropTypes.object,

    /**
     * Generic style overrides on the plot div
     */
    style: PropTypes.object,

    /**
     * className of the parent div
     */
    className: PropTypes.string,


    /**
     * Beta: If true, animate between updates using
     * plotly.js's `animate` function
     */
    animate: PropTypes.bool,

    /**
     * Beta: Object containing animation settings.
     * Only applies if `animate` is `true`
     */
    animation_options: PropTypes.object,

    /**
     * Plotly.js config options.
     * See https://plot.ly/javascript/configuration-options/
     * for more info.
     */
    config: PropTypes.shape({
        /**
         * no interactivity, for export or image generation
         */
        staticPlot: PropTypes.bool,

         /**
          * we can edit titles, move annotations, etc - sets all pieces of `edits`
          * unless a separate `edits` config item overrides individual parts
          */
        editable:  PropTypes.bool,

        /**
         * a set of editable properties
         */
        edits: PropTypes.shape({
            /**
             * annotationPosition: the main anchor of the annotation, which is the
             * text (if no arrow) or the arrow (which drags the whole thing leaving
             * the arrow length & direction unchanged)
             */
            annotationPosition: PropTypes.bool,

            /**
             * just for annotations with arrows, change the length and direction of the arrow
             */
            annotationTail: PropTypes.bool,

            annotationText: PropTypes.bool,

            axisTitleText: PropTypes.bool,

            colorbarPosition: PropTypes.bool,

            colorbarTitleText: PropTypes.bool,

            legendPosition: PropTypes.bool,

            /**
             * edit the trace name fields from the legend
             */
            legendText: PropTypes.bool,

            shapePosition: PropTypes.bool,

            /**
             * the global `layout.title`
             */
            titleText: PropTypes.bool
        }),

        /**
         * DO autosize once regardless of layout.autosize
         * (use default width or height values otherwise)
         */
        autosizable: PropTypes.bool,

        /**
         * set the length of the undo/redo queue
         */
        queueLength: PropTypes.number,

        /**
         * if we DO autosize, do we fill the container or the screen?
         */
        fillFrame: PropTypes.bool,

        /**
         * if we DO autosize, set the frame margins in percents of plot size
         */
        frameMargins: PropTypes.number,

        /**
         * mousewheel or two-finger scroll zooms the plot
         */
        scrollZoom: PropTypes.bool,

        /**
         * double click interaction (false, 'reset', 'autosize' or 'reset+autosize')
         */
        doubleClick: PropTypes.oneOf([
            false,
            'reset',
            'autosize',
            'reset+autosize'
        ]),

        /**
         * new users see some hints about interactivity
         */
        showTips: PropTypes.bool,

        /**
         * enable axis pan/zoom drag handles
         */
        showAxisDragHandles: PropTypes.bool,

        /**
         * enable direct range entry at the pan/zoom drag points
         * (drag handles must be enabled above)
         */
        showAxisRangeEntryBoxes: PropTypes.bool,

        /**
         * link to open this plot in plotly
         */
        showLink: PropTypes.bool,

        /**
         * if we show a link, does it contain data or just link to a plotly file?
         */
        sendData: PropTypes.bool,

        /**
         * text appearing in the sendData link
         */
        linkText: PropTypes.string,

        /**
         * display the mode bar (true, false, or 'hover')
         */
        displayModeBar: PropTypes.oneOf([
            true, false, 'hover'
        ]),

        /**
         * remove mode bar button by name.
         * All modebar button names at https://github.com/plotly/plotly.js/blob/master/src/components/modebar/buttons.js
         * Common names include:
         *  - sendDataToCloud
         * - (2D): zoom2d, pan2d, select2d, lasso2d, zoomIn2d, zoomOut2d, autoScale2d, resetScale2d
         * - (Cartesian): hoverClosestCartesian, hoverCompareCartesian
         * - (3D): zoom3d, pan3d, orbitRotation, tableRotation, handleDrag3d, resetCameraDefault3d, resetCameraLastSave3d, hoverClosest3d
         * - (Geo): zoomInGeo, zoomOutGeo, resetGeo, hoverClosestGeo
         * - hoverClosestGl2d, hoverClosestPie, toggleHover, resetViews
         */
        modeBarButtonsToRemove: PropTypes.array,

        /**
         * add mode bar button using config objects
         */
        modeBarButtonsToAdd: PropTypes.array,

        /**
         * fully custom mode bar buttons as nested array,
         * where the outer arrays represents button groups, and
         * the inner arrays have buttons config objects or names of default buttons
         */
        modeBarButtons: PropTypes.any,

        /**
         * add the plotly logo on the end of the mode bar
         */
        displaylogo: PropTypes.bool,

        /**
         * increase the pixel ratio for Gl plot images
         */
        plotGlPixelRatio: PropTypes.number,

        /**
         * URL to topojson files used in geo charts
         */
        topojsonURL: PropTypes.string,

        /**
         * Mapbox access token (required to plot mapbox trace types)
         * If using an Mapbox Atlas server, set this option to '',
         * so that plotly.js won't attempt to authenticate to the public Mapbox server.
         */
        mapboxAccessToken: PropTypes.any
    }),

    /**
     *
     */
    dashEvents: PropTypes.oneOf([
        'click',
        'hover',
        'selected',
        'relayout',
        'unhover'
    ]),

    /**
     * Function that updates the state tree.
     */
    setProps: PropTypes.func,

    /**
     * Function that fires events
     */
    dashFireEvent: PropTypes.func
}

PlotlyGraph.defaultProps = {
    clickData: null,
    hoverData: null,
    selectedData: null,
    relayoutData: null,
    figure: {data: [], layout: {}},
    animate: false,
    animation_options: {
        frame: {
            redraw: false
        },
        transition: {
            duration: 750,
            ease: 'cubic-in-out'
        }
    },
    clear_on_unhover: false,
    config: {
        staticPlot: false,
        editable: false,
        edits: {
            annotationPosition: false,
            annotationTail: false,
            annotationText: false,
            axisTitleText: false,
            colorbarPosition: false,
            colorbarTitleText: false,
            legendPosition: false,
            legendText: false,
            shapePosition: false,
            titleText: false
        },
        autosizable: false,
        queueLength: 0,
        fillFrame: false,
        frameMargins: 0,
        scrollZoom: false,
        doubleClick: 'reset+autosize',
        showTips: true,
        showAxisDragHandles: true,
        showAxisRangeEntryBoxes: true,
        showLink: false,
        sendData: true,
        linkText: 'Edit chart',
        showSources: false,
        displayModeBar: 'hover',
        modeBarButtonsToRemove: [],
        modeBarButtonsToAdd: [],
        modeBarButtons: false,
        displaylogo: true,
        plotGlPixelRatio: 2,
        topojsonURL: 'https://cdn.plot.ly/',
        mapboxAccessToken: null
    }
};
