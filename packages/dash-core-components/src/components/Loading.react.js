import React, {Component} from 'react';
import PropTypes from 'prop-types';
import GraphSpinner from '../fragments/Loading/spinners/GraphSpinner.jsx';
import DefaultSpinner from '../fragments/Loading/spinners/DefaultSpinner.jsx';
import CubeSpinner from '../fragments/Loading/spinners/CubeSpinner.jsx';
import CircleSpinner from '../fragments/Loading/spinners/CircleSpinner.jsx';
import DotSpinner from '../fragments/Loading/spinners/DotSpinner.jsx';
import {mergeRight} from 'ramda';

function getSpinner(spinnerType) {
    switch (spinnerType) {
        case 'graph':
            return GraphSpinner;
        case 'cube':
            return CubeSpinner;
        case 'circle':
            return CircleSpinner;
        case 'dot':
            return DotSpinner;
        default:
            return DefaultSpinner;
    }
}

const hiddenContainer = {visibility: 'hidden', position: 'relative'};

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

/**
 * A Loading component that wraps any other component and displays a spinner until the wrapped component has rendered.
 */
export default class Loading extends Component {
    render() {
        const {
            loading_state,
            color,
            className,
            style,
            parent_className,
            parent_style,
            fullscreen,
            debug,
            type: spinnerType,
        } = this.props;

        const isLoading = loading_state && loading_state.is_loading;
        const Spinner = isLoading && getSpinner(spinnerType);

        return (
            <div
                className={parent_className}
                style={
                    isLoading
                        ? mergeRight(hiddenContainer, parent_style)
                        : parent_style
                }
            >
                {this.props.children}
                <div style={isLoading ? coveringSpinner : {}}>
                    {isLoading && (
                        <Spinner
                            className={className}
                            style={style}
                            status={loading_state}
                            color={color}
                            debug={debug}
                            fullscreen={fullscreen}
                        />
                    )}
                </div>
            </div>
        );
    }
}

Loading._dashprivate_isLoadingComponent = true;

Loading.defaultProps = {
    type: 'default',
    color: '#119DFF',
};

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
     * Property that determines which spinner to show
     * one of 'graph', 'cube', 'circle', 'dot', or 'default'.
     */
    type: PropTypes.oneOf(['graph', 'cube', 'circle', 'dot', 'default']),

    /**
     * Boolean that makes the spinner display full-screen
     */
    fullscreen: PropTypes.bool,

    /**
     * If true, the spinner will display the component_name and prop_name
     * while loading
     */
    debug: PropTypes.bool,

    /**
     * Additional CSS class for the spinner root DOM node
     */
    className: PropTypes.string,

    /**
     *  Additional CSS class for the outermost dcc.Loading parent div DOM node
     */
    parent_className: PropTypes.string,

    /**
     * Additional CSS styling for the spinner root DOM node
     */
    style: PropTypes.object,

    /**
     * Additional CSS styling for the outermost dcc.Loading parent div DOM node
     */
    parent_style: PropTypes.object,

    /**
     * Primary colour used for the loading spinners
     */
    color: PropTypes.string,

    /**
     * Object that holds the loading state object coming from dash-renderer
     */
    loading_state: PropTypes.shape({
        /**
         * Determines if the component is loading or not
         */
        is_loading: PropTypes.bool,
        /**
         * Holds which property is loading
         */
        prop_name: PropTypes.string,
        /**
         * Holds the name of the component that is loading
         */
        component_name: PropTypes.string,
    }),
};
