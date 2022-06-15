import React from 'react';
import PropTypes from 'prop-types';


const StandardComponent = (props) => {
    const { id, children } = props;

    return (
        <div id={id}>
            {children}
        </div>
    )
}

StandardComponent.propTypes  = {
    id: PropTypes.string,
    children: PropTypes.node,
}

export default StandardComponent
