import PropTypes from 'prop-types';
import React from 'react';

/**
 * MyComponent description
 */
const MyStandardComponent = ({ id, style, value }) => (<div id={id} style={style}>{value}</div>);

MyStandardComponent.propTypes = {
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
    value: PropTypes.string
};

MyStandardComponent.defaultProps = {
    value: ''
};

export default MyStandardComponent;