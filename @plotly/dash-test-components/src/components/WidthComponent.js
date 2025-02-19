import PropTypes from 'prop-types';
import React, { Fragment } from 'react';

const WidthComponent = ({width = 0}) => (<Fragment>
    {width}
</Fragment>);

WidthComponent.propTypes = {
    id: PropTypes.string,
    width: PropTypes.number
};

export default WidthComponent;
