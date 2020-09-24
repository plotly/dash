import PropTypes from 'prop-types';
import React, { Fragment } from 'react';

const FragmentComponent = props => (<Fragment>
    {props.children}
</Fragment>);

FragmentComponent.propTypes = {
    children: PropTypes.node,
    id: PropTypes.string
};

FragmentComponent.defaultProps = {};

export default FragmentComponent;