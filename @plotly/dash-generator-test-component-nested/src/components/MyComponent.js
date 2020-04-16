import PropTypes from 'prop-types';
import React from 'react';

/**
 * MyComponent description
 */
const MyComponent = ({ id, value }) => (<div id={id}>{value}</div>);

MyComponent.propTypes = {
    /**
     * The id of the component
     */
    id: PropTypes.string,

    /**
     * The value to display
     */
    value: PropTypes.string
};

MyComponent.defaultProps = {
    value: ''
};

export default MyComponent;