import lazyLoadMathJax from '../utils/LazyLoader/third-party/mathjax';
import React, {Component} from 'react';
import {
    equals,
    filter,
    has,
    includes,
    isNil,
    mergeDeepRight,
    omit,
    path,
    type,
    clone,
} from 'ramda';
import PropTypes from 'prop-types';
import {graphPropTypes, graphDefaultProps} from '../components/Graph.react';

/* global Plotly:true */

import ResizeDetector from '../utils/ResizeDetector';
import LoadingElement from '../utils/LoadingElement';

/**
 * `autosize: true` causes Plotly.js to conform to the parent element size.
 * This is necessary for `dcc.Graph` call to `Plotly.Plots.resize(target)` to do something.
 *
 * Users can override this value for specific use-cases by explicitly passing `autoresize: true`
 * if `responsive` is not set to True.
 */
const RESPONSIVE_LAYOUT = {
    autosize: true,
    height: undefined,
    width: undefined,
};

const AUTO_LAYOUT = {};

const UNRESPONSIVE_LAYOUT = {
    autosize: false,
};

/**
 * `responsive: true` causes Plotly.js to resize the graph on `window.resize`.
 * This is necessary for `dcc.Graph` call to `Plotly.Plots.resize(target)` to do something.
 *
 * Users can override this value for specific use-cases by explicitly passing `responsive: false`
 * if `responsive` is not set to True.
 */
const RESPONSIVE_CONFIG = {
    responsive: true,
};

const AUTO_CONFIG = {};

const UNRESPONSIVE_CONFIG = {
    responsive: false,
};

const toPlainArray = value => {
    if (ArrayBuffer.isView(value)) {
        return Array.from(value);
    }
    if (Array.isArray(value)) {
        return value.map(toPlainArray);
    }
    return value;
};

const filterEventData = (gd, eventData, event) => {
    let filteredEventData;
    if (includes(event, ['click', 'hover', 'selected'])) {
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
        // Parcoords sends one flat point instead of a points array. Its
        // curveNumber is the line index and dataIndex is the trace index, so
        // reshape it to match other traces: curveNumber is the trace and
        // pointNumber is the line.
        const eventPoints = Array.isArray(eventData.points)
            ? eventData.points
            : [
                  {
                      ...eventData,
                      curveNumber: eventData.dataIndex,
                      pointNumber: eventData.curveNumber,
                  },
              ];

        for (let i = 0; i < eventPoints.length; i++) {
            const fullPoint = eventPoints[i];
            const pointData = filter(function (o) {
                return !includes(type(o), ['Object', 'Array']);
            }, fullPoint);

            // permit a bounding box to pass through, if present
            if (has('bbox', fullPoint)) {
                pointData.bbox = fullPoint.bbox;
            }

            if (
                has('curveNumber', fullPoint) &&
                has('customdata', data[pointData.curveNumber])
            ) {
                const customdata = data[pointData.curveNumber].customdata;
                // Binary (typed array) customdata is only decoded in the full
                // trace, so read it from there and fall back to the input.
                const customdataArray =
                    fullPoint.fullData?.customdata ?? customdata;
                if (has('pointNumber', fullPoint)) {
                    if (typeof fullPoint.pointNumber === 'number') {
                        pointData.customdata =
                            customdataArray[fullPoint.pointNumber];
                    } else if (
                        !fullPoint.pointNumber &&
                        fullPoint.data.mode.includes('lines')
                    ) {
                        pointData.customdata = customdataArray;
                    }
                } else if (has('pointNumbers', fullPoint)) {
                    pointData.customdata = fullPoint.pointNumbers.map(function (
                        point
                    ) {
                        return customdataArray[point];
                    });
                }
                // Typed arrays would serialize as objects, so send plain arrays.
                pointData.customdata = toPlainArray(pointData.customdata);
            }

            // specific to histogram. see https://github.com/plotly/plotly.js/pull/2113/
            if (has('pointNumbers', fullPoint)) {
                pointData.pointNumbers = fullPoint.pointNumbers;
            }

            points[i] = pointData;
        }
        filteredEventData = {points};

        const includeXYVals =
            (event === 'hover' && gd._fullLayout.hoveranywhere === true) ||
            (event === 'click' && gd._fullLayout.clickanywhere === true);

        if (includeXYVals) {
            ['xvals', 'yvals', 'xPixel', 'yPixel'].forEach(key => {
                if (has(key, eventData)) {
                    filteredEventData[key] = eventData[key];
                }
            });

            if (has('xaxes', eventData)) {
                filteredEventData.xaxes_id = eventData.xaxes[0]._id;
            }

            if (has('yaxes', eventData)) {
                filteredEventData.yaxes_id = eventData.yaxes[0]._id;
            }
        }
    } else if (event === 'relayout' || event === 'restyle') {
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

// layoutUIControlPatterns in plotly.js src/plot_api/plot_api.js: the GUI
// edits plotly.js keeps across figure updates while their uirevision holds
const UIREVISION_PATTERNS = [
    {pattern: /^hiddenlabels/, attr: 'legend.uirevision'},
    {pattern: /^((x|y)axis\d*)\.((auto)?range|title\.text)/},
    {pattern: /axis\d*\.showspikes$/, attr: 'modebar.uirevision'},
    {pattern: /(hover|drag)mode$/, attr: 'modebar.uirevision'},
    {pattern: /^(scene\d*)\.camera/},
    {pattern: /^(geo\d*)\.(projection|center|fitbounds)/},
    {pattern: /^(ternary\d*\.[abc]axis)\.(min|title\.text)$/},
    {pattern: /^(polar\d*\.radialaxis)\.((auto)?range|angle|title\.text)/},
    {pattern: /^(polar\d*\.angularaxis)\.rotation/},
    {pattern: /^(map\d*)\.(center|zoom|bearing|pitch)/},
    {pattern: /^legend\.(x|y)$/, attr: 'editrevision'},
    {pattern: /^(shapes|annotations)/, attr: 'editrevision'},
    {pattern: /^selections/, attr: 'selectionrevision'},
    {pattern: /^title\.text$/, attr: 'editrevision'},
];

const getRevisionAttr = attr => {
    for (const {pattern, attr: revisionAttr} of UIREVISION_PATTERNS) {
        const match = attr.match(pattern);
        if (match) {
            return revisionAttr || `${match[1]}.uirevision`;
        }
    }
    return null;
};

// 'shapes[1].x0' -> ['shapes', 1, 'x0']
const toPath = attr =>
    attr.split('.').flatMap(part =>
        part
            .split(/\[(\d+)\]/)
            .filter(segment => segment !== '')
            .map((segment, i) => (i ? Number(segment) : segment))
    );

// Same inheritance as getNewRev in plotly.js
const getNewRevision = (layout, revisionAttr) => {
    const keys = toPath(revisionAttr);
    const revision = path(keys, layout);
    if (revision !== undefined) {
        return revision;
    }
    for (let depth = keys.length - 2; depth > 0; depth--) {
        const inherited = path([...keys.slice(0, depth), 'uirevision'], layout);
        if (inherited !== undefined) {
            return inherited;
        }
    }
    return layout.uirevision;
};

// Only sets inside existing containers, never creates them
const setPath = (container, keys, value) => {
    const parent = path(keys.slice(0, -1), container);
    if (typeof parent !== 'object' || parent === null) {
        return;
    }
    const last = keys[keys.length - 1];
    if (Array.isArray(parent) && last >= parent.length) {
        return;
    }
    if (value === undefined && !Array.isArray(parent)) {
        delete parent[last];
    } else {
        parent[last] = value;
    }
};

/**
 * Graph can be used to render any plotly.js-powered data visualization.
 *
 * You can define callbacks based on user interaction with Graphs such as
 * hovering, clicking or selecting
 */
class PlotlyGraph extends Component {
    constructor(props) {
        super(props);
        this.gd = React.createRef();
        this._hasPlotted = false;
        this._prevGd = null;
        this._queue = Promise.resolve();
        this._pendingFigures = [];

        this.parentElement = React.createRef();

        this.bindEvents = this.bindEvents.bind(this);
        this.getConfig = this.getConfig.bind(this);
        this.getConfigOverride = this.getConfigOverride.bind(this);
        this.getLayout = this.getLayout.bind(this);
        this.getLayoutOverride = this.getLayoutOverride.bind(this);
        this.graphResize = this.graphResize.bind(this);
        this.isResponsive = this.isResponsive.bind(this);
        this.amendTraces = this.amendTraces.bind(this);

        this.state = {override: {}, originals: {}};
        this._syncedEdits = {};
    }

    plot(props) {
        let {figure, config} = props;
        const {animate, animation_options, responsive, mathjax} = props;

        const gd = this.gd.current;
        figure = props._dashprivate_transformFigure(figure, gd);
        config = props._dashprivate_transformConfig(config, gd);

        const configClone = this.getConfig(config, responsive);
        // add typesetMath | not exposed to the dash API
        configClone.typesetMath = mathjax;

        const animating =
            animate &&
            this._hasPlotted &&
            figure.data.length === gd.data.length;

        const layout = this.getLayout(figure?.layout, responsive);
        this.applySyncedEdits(layout, animating);

        const figureClone = {
            data: figure?.data,
            layout,
            frames: figure?.frames,
            config: configClone,
        };

        if (animating) {
            // in case we've have figure frames,
            // we need to recreate frames before animation
            if (figure.frames) {
                return Plotly.deleteFrames(gd)
                    .then(() => Plotly.addFrames(gd, figure.frames))
                    .then(() =>
                        Plotly.animate(gd, figureClone, animation_options)
                    );
            }
            return Plotly.animate(gd, figureClone, animation_options);
        }

        gd.classList.add('dash-graph--pending');

        return lazyLoadMathJax(mathjax)
            .then(() => {
                const gd = this.gd.current;
                return gd && Plotly.react(gd, figureClone);
            })
            .then(() => {
                const gd = this.gd.current;

                // double-check gd hasn't been unmounted
                if (!gd) {
                    return;
                }

                gd.classList.remove('dash-graph--pending');

                // in case we've made a new DOM element, transfer events
                if (this._hasPlotted && gd !== this._prevGd) {
                    if (this._prevGd && this._prevGd.removeAllListeners) {
                        this._prevGd.removeAllListeners();
                        Plotly.purge(this._prevGd);
                    }
                    this._hasPlotted = false;
                }

                if (!this._hasPlotted) {
                    this.bindEvents();
                    this.graphResize(true);
                    this._hasPlotted = true;
                    this._prevGd = gd;
                }
            });
    }

    amendTraces(p, oldProps, newProps) {
        const {prependData: oldPrepend, extendData: oldExtend} = oldProps;
        const {prependData: newPrepend, extendData: newExtend} = newProps;
        const _this = this;

        function mergeTraces(props, dataKey, plotlyFnKey) {
            const clearState = props.clearState;
            const dataArray = props[dataKey];

            let _p = Promise.resolve();

            dataArray.forEach(data => {
                let updateData, traceIndices, maxPoints;
                if (Array.isArray(data) && typeof data[0] === 'object') {
                    [updateData, traceIndices, maxPoints] = data;
                } else {
                    updateData = data;
                }

                if (!traceIndices) {
                    function getFirstProp(data) {
                        return data[Object.keys(data)[0]];
                    }

                    function generateIndices(data) {
                        return Array.from(
                            Array(getFirstProp(data).length).keys()
                        );
                    }
                    traceIndices = generateIndices(updateData);
                }

                _p = _p.then(() => {
                    const gd = _this.gd.current;
                    return (
                        gd &&
                        Plotly[plotlyFnKey](
                            gd,
                            updateData,
                            traceIndices,
                            maxPoints
                        )
                    );
                });
            });

            return _p.then(() => clearState(dataKey));
        }

        let modified = false;

        if (newPrepend?.length && oldPrepend !== newPrepend) {
            modified = true;
            p = p.then(() =>
                mergeTraces(newProps, 'prependData', 'prependTraces')
            );
        }

        if (newExtend?.length && oldExtend !== newExtend) {
            modified = true;
            p = p.then(() =>
                mergeTraces(newProps, 'extendData', 'extendTraces')
            );
        }

        if (modified) {
            p = p.then(() =>
                newProps._dashprivate_onFigureModified(newProps.figure)
            );
        }

        return p;
    }

    getConfig(config, responsive) {
        return mergeDeepRight(config, this.getConfigOverride(responsive));
    }

    getLayout(originalLayout, responsive) {
        if (!originalLayout) {
            return originalLayout;
        }
        // Clone layout to avoid mutating the original (important for Patch)
        const layout = clone(originalLayout);
        const override = this.getLayoutOverride(responsive);
        const {override: prev_override, originals: prev_originals} = this.state;
        // Store the original data that we're about to override
        const originals = {};
        for (const key in override) {
            if (layout[key] !== prev_override[key]) {
                originals[key] = layout[key];
            } else if (prev_originals.hasOwnProperty(key)) {
                originals[key] = prev_originals[key];
            }
        }
        this.setState({override, originals});
        // Undo the previous override, but only for keys that the user did not change
        for (const key in prev_originals) {
            if (layout[key] === prev_override[key]) {
                layout[key] = prev_originals[key];
            }
        }
        // Apply the current override
        for (const key in override) {
            layout[key] = override[key];
        }
        return layout;
    }

    /*
     * The plotly_relayout handler copies GUI edits (zoom, pan, ...) into the
     * figure prop. If Plotly.react gets them as input, plotly.js takes them as
     * the new starting point and drops them from its uirevision bookkeeping
     * (_preGUI), so a later figure without them resets the view. While a
     * synced value is still in the figure and its uirevision is unchanged,
     * give plotly.js the value from before the edit so it keeps the edit
     * itself. Plotly.animate does not apply uirevision, so there the value
     * from before the edit is replaced by the edit instead.
     */
    applySyncedEdits(layout, animating) {
        const fullLayout = this.gd.current?._fullLayout;
        const preGUI = fullLayout?._preGUI;
        if (!layout || !preGUI) {
            return;
        }
        for (const [attr, syncedValues] of Object.entries(this._syncedEdits)) {
            if (!(attr in preGUI)) {
                delete this._syncedEdits[attr];
                continue;
            }
            const revisionAttr = getRevisionAttr(attr);
            const oldRevision = path(toPath(revisionAttr), fullLayout);
            if (
                !oldRevision ||
                getNewRevision(layout, revisionAttr) !== oldRevision
            ) {
                continue;
            }
            const keys = toPath(attr);
            const value = path(keys, layout);
            const original = preGUI[attr] ?? undefined;
            if (animating) {
                if (equals(value, original)) {
                    setPath(
                        layout,
                        keys,
                        clone(syncedValues[syncedValues.length - 1])
                    );
                }
                continue;
            }
            // Earlier syncs may still be queued for plotting
            const index = syncedValues.findIndex(synced =>
                equals(value, synced)
            );
            if (index !== -1) {
                this._syncedEdits[attr] = syncedValues.slice(index);
                setPath(layout, keys, original);
            }
        }
    }

    trackSyncedEdits(updates) {
        const preGUI = this.gd.current?._fullLayout?._preGUI ?? {};
        for (const attr of Object.keys(preGUI)) {
            const keys = toPath(attr);
            if (keys[0] in updates && getRevisionAttr(attr)) {
                this._syncedEdits[attr] = [
                    ...(this._syncedEdits[attr] ?? []),
                    path(keys, updates),
                ];
            }
        }
    }

    getConfigOverride(responsive) {
        switch (responsive) {
            case false:
                return UNRESPONSIVE_CONFIG;
            case true:
                return RESPONSIVE_CONFIG;
            default:
                return AUTO_CONFIG;
        }
    }

    getLayoutOverride(responsive) {
        switch (responsive) {
            case false:
                return UNRESPONSIVE_LAYOUT;
            case true:
                return RESPONSIVE_LAYOUT;
            default:
                return AUTO_LAYOUT;
        }
    }

    isResponsive(props) {
        const {config, figure, responsive} = props;

        if (type(responsive) === 'Boolean') {
            return responsive;
        }

        return Boolean(
            config.responsive &&
                (!figure.layout ||
                    ((figure.layout.autosize ||
                        isNil(figure.layout.autosize)) &&
                        (isNil(figure.layout.height) ||
                            isNil(figure.layout.width))))
        );
    }

    graphResize(force = false) {
        if (!force && !this.isResponsive(this.props)) {
            return;
        }

        const gd = this.gd.current;
        if (!gd) {
            return;
        }

        gd.classList.add('dash-graph--pending');

        // Calling resize enables layout.autosize in plotly.js
        Plotly.Plots.resize(gd)
            .catch(() => {})
            .finally(() => gd.classList.remove('dash-graph--pending'));
    }

    bindEvents() {
        const {
            setProps,
            clear_on_unhover,
            relayoutData,
            restyleData,
            hoverData,
            selectedData,
        } = this.props;

        const gd = this.gd.current;

        gd.on('plotly_click', eventData => {
            const clickData = filterEventData(gd, eventData, 'click');
            if (!isNil(clickData)) {
                // Add timestamp to ensure each click is unique (for DashWrapper deduplication)
                clickData.timestamp = Date.now();
                setProps({clickData});
            }
        });
        gd.on('plotly_clickannotation', eventData => {
            const clickAnnotationData = omit(
                ['event', 'fullAnnotation'],
                eventData
            );
            // Add timestamp to ensure each click is unique (for DashWrapper deduplication)
            clickAnnotationData.timestamp = Date.now();
            setProps({clickAnnotationData});
        });
        gd.on('plotly_hover', eventData => {
            const hover = filterEventData(gd, eventData, 'hover');
            if (!isNil(hover) && !equals(hover, hoverData)) {
                setProps({hoverData: hover});
            }
        });
        gd.on('plotly_selected', eventData => {
            const selected = filterEventData(gd, eventData, 'selected');
            if (!isNil(selected) && !equals(selected, selectedData)) {
                setProps({selectedData: selected});
            }
        });
        gd.on('plotly_deselect', () => {
            setProps({selectedData: null});
        });
        gd.on('plotly_relayout', eventData => {
            const relayout = filterEventData(gd, eventData, 'relayout');
            if (!isNil(relayout) && !equals(relayout, relayoutData)) {
                setProps({relayoutData: relayout});
            }
            // Sync user-driven layout changes (pan/zoom ranges, edited
            // shapes, annotations, ...) from gd.layout back to the figure
            // prop. This is needed because getLayout() clones layout to
            // prevent mutation issues, so plotly.js only updates its own
            // copy and the figure prop (used as the base for Patch
            // updates) would otherwise go stale.
            if (eventData && gd.layout) {
                // React may batch several relayouts before delivering props.
                // Build on the latest sync rather than losing its changes.
                const figure =
                    this._pendingFigures[this._pendingFigures.length - 1] ??
                    this.props.figure ??
                    {};
                const updates = {};
                for (const eventKey of Object.keys(eventData)) {
                    // 'xaxis.range[0]' -> 'xaxis', 'shapes[1].x0' -> 'shapes'
                    const key = eventKey.split('.')[0].split('[')[0];
                    if (
                        // autosize/width/height relayouts come from the
                        // resize machinery, not from user interactions.
                        !includes(key, ['autosize', 'width', 'height']) &&
                        !(key in updates) &&
                        !equals(figure?.layout?.[key], gd.layout[key])
                    ) {
                        updates[key] = clone(gd.layout[key]);
                    }
                }
                if (Object.keys(updates).length) {
                    this.trackSyncedEdits(updates);
                    const syncedFigure = {
                        ...figure,
                        layout: {
                            ...figure?.layout,
                            ...updates,
                        },
                    };
                    this._pendingFigures.push(syncedFigure);
                    setProps({figure: syncedFigure});
                }
            }
        });
        gd.on('plotly_restyle', eventData => {
            const restyle = filterEventData(gd, eventData, 'restyle');
            if (!isNil(restyle) && !equals(restyle, restyleData)) {
                setProps({restyleData: restyle});
            }
        });
        gd.on('plotly_unhover', () => {
            if (clear_on_unhover) {
                setProps({hoverData: null});
            }
        });
    }

    componentDidMount() {
        const p = this.plot(this.props);
        this._queue = this.amendTraces(p, {}, this.props);
    }

    componentWillUnmount() {
        const gd = this.gd.current;
        if (gd && gd.removeAllListeners) {
            gd.removeAllListeners();
            if (this._hasPlotted) {
                Plotly.purge(gd);
            }
        }
    }

    shouldComponentUpdate(nextProps) {
        return (
            this.props.id !== nextProps.id ||
            JSON.stringify(this.props.style) !== JSON.stringify(nextProps.style)
        );
    }

    UNSAFE_componentWillReceiveProps(nextProps) {
        const idChanged = this.props.id !== nextProps.id;
        if (idChanged) {
            this._pendingFigures = [];
            this._syncedEdits = {};
            /*
             * then the dom needs to get re-rendered with a new ID.
             * the graph will get updated in componentDidUpdate
             */
            return;
        }

        if (this.props.figure !== nextProps.figure) {
            // An acknowledgement may skip batched figures or arrive before
            // a later sync. An external figure supersedes all pending syncs.
            const syncedIndex = this._pendingFigures.indexOf(nextProps.figure);
            this._pendingFigures =
                syncedIndex === -1
                    ? []
                    : this._pendingFigures.slice(syncedIndex + 1);
        }

        let p = this._queue;

        if (
            this.props.mathjax !== nextProps.mathjax ||
            this.props.figure !== nextProps.figure ||
            this.props._dashprivate_transformConfig !==
                nextProps._dashprivate_transformConfig ||
            this.props._dashprivate_transformFigure !==
                nextProps._dashprivate_transformFigure
        ) {
            p = p.then(() => this.plot(nextProps));
        }

        this._queue = this.amendTraces(p, this.props, nextProps);
    }

    componentDidUpdate(prevProps) {
        if (
            prevProps.id !== this.props.id ||
            prevProps.mathjax !== this.props.mathjax
        ) {
            this._queue = this._queue.then(() => this.plot(this.props));
        }
    }

    render() {
        const {className, id, loading_state, style = {}} = this.props;
        if (this.isResponsive(this.props)) {
            style.height ||= '100%';
        }

        let Container = LoadingElement;
        const containerProps = {
            className,
            id,
            key: id,
            ref: this.parentElement,
            style,
        };
        if (!window.dash_component_api) {
            Container = 'div';
            containerProps['data-dash-is-loading'] =
                loading_state?.is_loading || undefined;
        }

        return (
            <Container {...containerProps}>
                <ResizeDetector
                    onResize={this.graphResize}
                    targets={[this.parentElement, this.gd]}
                />
                <div ref={this.gd} style={{height: '100%', width: '100%'}} />
            </Container>
        );
    }
}

PlotlyGraph.propTypes = {
    ...graphPropTypes,
    prependData: PropTypes.arrayOf(
        PropTypes.oneOfType([PropTypes.array, PropTypes.object])
    ),
    extendData: PropTypes.arrayOf(
        PropTypes.oneOfType([PropTypes.array, PropTypes.object])
    ),
    clearState: PropTypes.func.isRequired,
};

PlotlyGraph.defaultProps = {
    ...graphDefaultProps,
    prependData: [],
    extendData: [],
};

export default PlotlyGraph;
