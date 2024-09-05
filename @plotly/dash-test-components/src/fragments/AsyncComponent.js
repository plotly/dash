import PropTypes from 'prop-types';
import React from 'react';

/**
 * MyComponent description
 */
const AsyncComponent = ({ id, value }) => <div id={id}>{value}</div>;

AsyncComponent.propTypes = {
    id: PropTypes.string,
    value: PropTypes.string
};

AsyncComponent.defaultProps = {};

export default AsyncComponent;
