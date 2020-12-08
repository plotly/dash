import PropTypes from 'prop-types';
import React, { Fragment } from 'react';

const WidthComponent = props => (<Fragment>
    {props.width}
</Fragment>);

WidthComponent.propTypes = {
    id: PropTypes.string,
    width: PropTypes.number
};

WidthComponent.defaultProps = {
    width: 0
};

export default WidthComponent;