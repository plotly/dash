import React from 'react';
import PropTypes from 'prop-types';


const ComponentAsProp = (props) => {
    const { element, id } = props;
    return (
        <div id={id}>
            {element}
        </div>
    )
}

ComponentAsProp.propTypes = {
    id: PropTypes.string,
    element: PropTypes.node,
}

export default ComponentAsProp;
