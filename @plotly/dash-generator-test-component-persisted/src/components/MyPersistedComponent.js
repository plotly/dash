import PropTypes from 'prop-types';
import React from 'react';

/**
 * MyComponent description
 */
const MyPersistedComponent = ({ id, value, value2, persistence, persisted_props, persistence_type }) => 
(<div id={id}>{value}<br></br>{value2}</div>);

MyPersistedComponent.propTypes = {
    /**
     * The id of the component
     */
    id: PropTypes.string,


    /**
     * The value to display
     */
    value: PropTypes.string,

    /**
     * The value to display
     */
    value2: PropTypes.string,

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
        PropTypes.oneOf(['value', 'value2'])
    ),

    /**
     * Where persisted user changes will be stored:
     * memory: only kept in memory, reset on page refresh.
     * local: window.localStorage, data is kept after the browser quit.
     * session: window.sessionStorage, data is cleared once the browser quit.
     */
    persistence_type: PropTypes.oneOf(['local', 'session', 'memory']),
};

MyPersistedComponent.persistenceTransforms = {
      value: {
        extract: propValue => {
            if (!(propValue === null || propValue === undefined)) {
                return str.toUpperCase(propValue);
            }
            return propValue;
        },
        apply: storedValue => storedValue,
       
    },
};

MyPersistedComponent.defaultProps = {
    value: '',
    value2: '',
    persisted_props: ['value', 'value2'],
    persistence_type: 'local',
};

export default MyPersistedComponent;