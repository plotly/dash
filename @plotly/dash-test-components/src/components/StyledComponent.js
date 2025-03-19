import PropTypes from 'prop-types';
import React from 'react';

/**
 * MyComponent description
 */
const StyledComponent = ({ id, style, value = '' }) => (<div id={id} style={style}>{value}</div>);

StyledComponent.propTypes = {
    /**
     * The id of the component
     */
    id: PropTypes.string,

    /**
     * The style
     */
    style: PropTypes.object,

    /**
     * The value to display
     */
    value: PropTypes.string
};

export default StyledComponent;
