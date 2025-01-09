import React, {useState, useRef, useMemo, useEffect} from 'react';
import {equals, concat, includes, toPairs, any} from 'ramda';
import PropTypes from 'prop-types';

import GraphSpinner from '../fragments/Loading/spinners/GraphSpinner.jsx';
import DefaultSpinner from '../fragments/Loading/spinners/DefaultSpinner.jsx';
import CubeSpinner from '../fragments/Loading/spinners/CubeSpinner.jsx';
import CircleSpinner from '../fragments/Loading/spinners/CircleSpinner.jsx';
import DotSpinner from '../fragments/Loading/spinners/DotSpinner.jsx';

const spinnerComponentOptions = {
    graph: GraphSpinner,
    cube: CubeSpinner,
    circle: CircleSpinner,
    dot: DotSpinner,
};

const getSpinner = spinnerType =>
    spinnerComponentOptions[spinnerType] || DefaultSpinner;

const coveringSpinner = {
    visibility: 'visible',
    position: 'absolute',
    top: '0',
    height: '100%',
    width: '100%',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
};

const loadingSelector = (componentPath, targetComponents) => state => {
    let stringPath = JSON.stringify(componentPath);
    // Remove the last ] for easy match
    stringPath = stringPath.substring(0, stringPath.length - 1);
    const loadingChildren = toPairs(state.loading).reduce(
        (acc, [path, load]) => {
            if (path.startsWith(stringPath) && load.length) {
                if (
                    targetComponents &&
                    !any(l => {
                        const target = targetComponents[l.id];
                        if (!target) {
                            return false;
                        }
                        if (Array.isArray(target)) {
                            return includes(l.property, target);
                        }
                        return l.property === target;
                    }, load)
                ) {
                    return acc;
                }
                return concat(acc, load);
            }
            return acc;
        },
        []
    );
    if (loadingChildren.length) {
        return loadingChildren;
    }
    return null;
};

function Loading({
    children,
    display = 'auto',
    color = '#119DFF',
    id,
    className,
    style,
    parent_className,
    parent_style,
    overlay_style,
    fullscreen,
    debug,
    show_initially = true,
    type: spinnerType,
    delay_hide = 0,
    delay_show = 0,
    target_components,
    custom_spinner,
}) {
    const ctx = window.dash_component_api.useDashContext();
    const loading = ctx.useSelector(
        loadingSelector(ctx.componentPath, target_components),
        equals
    );

    const [showSpinner, setShowSpinner] = useState(show_initially);
    const dismissTimer = useRef();
    const showTimer = useRef();

    const containerStyle = useMemo(() => {
        if (showSpinner) {
            return {visibility: 'hidden', ...overlay_style, ...parent_style};
        }
        return parent_style;
    }, [showSpinner, parent_style]);

    useEffect(() => {
        if (display === 'show' || display === 'hide') {
            setShowSpinner(display === 'show');
            return;
        }

        if (loading) {
            // if component is currently loading and there's a dismiss timer active
            // we need to clear it.
            if (dismissTimer.current) {
                dismissTimer.current = clearTimeout(dismissTimer.current);
            }
            // if component is currently loading but the spinner is not showing and
            // there is no timer set to show, then set a timeout to show
            if (!showSpinner && !showTimer.current) {
                showTimer.current = setTimeout(() => {
                    setShowSpinner(true);
                    showTimer.current = null;
                }, delay_show);
            }
        } else {
            // if component is not currently loading and there's a show timer
            // active we need to clear it
            if (showTimer.current) {
                showTimer.current = clearTimeout(showTimer.current);
            }
            // if component is not currently loading and the spinner is showing and
            // there's no timer set to dismiss it, then set a timeout to hide it
            if (showSpinner && !dismissTimer.current) {
                dismissTimer.current = setTimeout(() => {
                    setShowSpinner(false);
                    dismissTimer.current = null;
                }, delay_hide);
            }
        }
    }, [delay_hide, delay_show, loading, display, showSpinner]);

    const Spinner = showSpinner && getSpinner(spinnerType);

    return (
        <div
            style={{position: 'relative', ...parent_style}}
            className={parent_className}
        >
            <div className={parent_className} style={containerStyle}>
                {children}
            </div>
            <div id={id} style={showSpinner ? coveringSpinner : {}}>
                {showSpinner &&
                    (custom_spinner || (
                        <Spinner
                            className={className}
                            style={style}
                            status={loading}
                            color={color}
                            debug={debug}
                            fullscreen={fullscreen}
                        />
                    ))}
            </div>
        </div>
    );
}

Loading.propTypes = {
    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id: PropTypes.string,

    /**
     * Array that holds components to render
     */
    children: PropTypes.oneOfType([
        PropTypes.arrayOf(PropTypes.node),
        PropTypes.node,
    ]),

    /**
     * Property that determines which built-in spinner to show
     * one of 'graph', 'cube', 'circle', 'dot', or 'default'.
     */
    type: PropTypes.oneOf(['graph', 'cube', 'circle', 'dot', 'default']),

    /**
     * Boolean that makes the built-in spinner display full-screen
     */
    fullscreen: PropTypes.bool,

    /**
     * If true, the built-in spinner will display the component_name and prop_name
     * while loading
     */
    debug: PropTypes.bool,

    /**
     * Additional CSS class for the built-in spinner root DOM node
     */
    className: PropTypes.string,

    /**
     *  Additional CSS class for the outermost dcc.Loading parent div DOM node
     */
    parent_className: PropTypes.string,

    /**
     * Additional CSS styling for the built-in spinner root DOM node
     */
    style: PropTypes.object,

    /**
     * Additional CSS styling for the outermost dcc.Loading parent div DOM node
     */
    parent_style: PropTypes.object,
    /**
     * Additional CSS styling for the spinner overlay. This is applied to the
     * dcc.Loading children while the spinner is active.  The default is `{'visibility': 'hidden'}`
     */
    overlay_style: PropTypes.object,

    /**
     * Primary color used for the built-in loading spinners
     */
    color: PropTypes.string,

    /**
     * Setting display to  "show" or "hide"  will override the loading state coming from dash-renderer
     */
    display: PropTypes.oneOf(['auto', 'show', 'hide']),

    /**
     * Add a time delay (in ms) to the spinner being removed to prevent flickering.
     */
    delay_hide: PropTypes.number,

    /**
     * Add a time delay (in ms) to the spinner being shown after the loading_state
     * is set to True.
     */
    delay_show: PropTypes.number,

    /**
     * Whether the Spinner should show on app start-up before the loading state
     * has been determined. Default True.  Use when also setting `delay_show`.
     */
    show_initially: PropTypes.bool,

    /**
     * Specify component and prop to trigger showing the loading spinner
     * example: `{"output-container": "children", "grid": ["rowData", "columnDefs]}`
     *
     */
    target_components: PropTypes.objectOf(
        PropTypes.oneOfType([
            PropTypes.string,
            PropTypes.arrayOf(PropTypes.string),
        ])
    ),

    /**
     *  Component to use rather than the built-in spinner specified in the `type` prop.
     *
     */
    custom_spinner: PropTypes.node,
};

export default Loading;
