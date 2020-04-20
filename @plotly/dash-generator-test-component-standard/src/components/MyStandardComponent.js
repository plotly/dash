import PropTypes from 'prop-types';
import React from 'react';

/**
 * MyComponent description
 */
const MyStandardComponent = ({ id, value }) => (<div id={id}>{value}</div>);

MyStandardComponent.propTypes = {
    /**
     * The id of the component
     */
    id: PropTypes.string,

    /**
     * The value to display
     */
    value: PropTypes.string
};

MyStandardComponent.defaultProps = {
    value: ''
};

export default MyStandardComponent;