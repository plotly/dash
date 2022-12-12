import PropTypes from 'prop-types';
import React, { Fragment } from 'react';

const CollapseComponent = props => (<Fragment>
    {props.display ? props.children : null}
</Fragment>);

CollapseComponent.propTypes = {
    children: PropTypes.node,
    display: PropTypes.bool,
    id: PropTypes.string
};

CollapseComponent.defaultProps = {
    display: false
};

export default CollapseComponent;
