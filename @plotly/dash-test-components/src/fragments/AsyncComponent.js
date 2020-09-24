import PropTypes from 'prop-types';
import React, { Fragment } from 'react';
import { asyncDecorator } from '@plotly/dash-component-plugins';

/**
 * MyComponent description
 */
const AsyncComponent = ({ value }) => (<Fragment>
    {value}
</Fragment>);

AsyncComponent.propTypes = {
    id: PropTypes.string,
    value: PropTypes.string
};

AsyncComponent.defaultProps = {};

export default AsyncComponent;