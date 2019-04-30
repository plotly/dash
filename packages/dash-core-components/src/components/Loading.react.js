import React, {Component} from 'react';
import PropTypes from 'prop-types';
import GraphSpinner from '../fragments/Loading/spinners/GraphSpinner.jsx';
import DefaultSpinner from '../fragments/Loading/spinners/DefaultSpinner.jsx';
import CubeSpinner from '../fragments/Loading/spinners/CubeSpinner.jsx';
import CircleSpinner from '../fragments/Loading/spinners/CircleSpinner.jsx';
import DotSpinner from '../fragments/Loading/spinners/DotSpinner.jsx';
import {type} from 'ramda';

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
            fullscreen,
            debug,
            type: spinnerType,
        } = this.props;

        if (loading_state && loading_state.is_loading) {
            const Spinner = getSpinner(spinnerType);
            return (
                <Spinner
                    className={className}
                    style={style}
                    status={loading_state}
                    color={color}
                    debug={debug}
                    fullscreen={fullscreen}
                />
            );
        }

        if (
            type(this.props.children) !== 'Object' ||
            type(this.props.children) !== 'Function'
        ) {
            return <div className={className}>{this.props.children}</div>;
        }
        return this.props.children;
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
     * Property that determines which spinner to show - one of 'graph', 'cube', 'circle', 'dot', or 'default'.
     */
    type: PropTypes.oneOf(['graph', 'cube', 'circle', 'dot', 'default']),

    /**
     * Boolean that determines if the loading spinner will be displayed full-screen or not
     */
    fullscreen: PropTypes.bool,

    /**
     * Boolean that determines if the loading spinner will display the status.prop_name and component_name
     */
    debug: PropTypes.bool,

    /**
     * Additional CSS class for the root DOM node
     */
    className: PropTypes.string,

    /**
     * Additional CSS styling for the root DOM node
     */
    style: PropTypes.object,

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
