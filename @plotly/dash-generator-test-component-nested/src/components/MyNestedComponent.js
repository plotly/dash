import PropTypes from 'prop-types';
import React from 'react';

/**
 * MyNestedComponent description
 */
const MyNestedComponent = ({ id, value }) => (<div id={id}>{value}</div>);

MyNestedComponent.propTypes = {
    /**
     * The id of the component
     */
    id: PropTypes.string,

    /**
     * The value to display
     */
    value: PropTypes.string
};

MyNestedComponent.defaultProps = {
    value: ''
};

export default MyNestedComponent;