import React from 'react';
import PropTypes from 'prop-types';


const ComponentAsProp = (props) => {
    const { element, elements, id } = props;
    return (
        <div id={id}>
            {elements || element}
        </div>
    )
}

ComponentAsProp.propTypes = {
    id: PropTypes.string,
    element: PropTypes.node,

    elements: PropTypes.arrayOf(PropTypes.node),
}

export default ComponentAsProp;
