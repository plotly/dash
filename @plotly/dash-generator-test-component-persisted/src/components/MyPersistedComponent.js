import PropTypes from 'prop-types';
import React from 'react';

/**
 * MyComponent description
 */
const MyPersistedComponent = ({ id, style, value }) => (<div id={id} style={style}>{value}</div>);

MyPersistedComponent.propTypes = {
    /**
     * The id of the component
     */
    id: PropTypes.string,

    /**
     * The style
     */
    style: PropTypes.shape,

    /**
     * The value to display
     */
    value: PropTypes.string,

    persistence: PropTypes.oneOfType([
        PropTypes.bool,
        PropTypes.string,
        PropTypes.number,
    ]),

    /**
     * Properties whose user interactions will persist after refreshing the
     * component or the page.
     */
    persisted_props: PropTypes.arrayOf(
        PropTypes.oneOf(['value'])
    ),

    /**
     * Where persisted user changes will be stored:
     * memory: only kept in memory, reset on page refresh.
     * local: window.localStorage, data is kept after the browser quit.
     * session: window.sessionStorage, data is cleared once the browser quit.
     */
    persistence_type: PropTypes.oneOf(['local', 'session', 'memory']),
};

MyPersistedComponent.defaultProps = {
    value: '',
    persisted_props: ['value'],
    persistence_type: 'local',
};

export default MyPersistedComponent;