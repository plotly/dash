import React from 'react';
import PropTypes from 'prop-types';


const ComponentAsProp = (props) => {
    const { element, elements, id, shapeEl } = props;
    return (
        <div id={id}>
            {shapeEl && shapeEl.header}
            {elements || element}
            {shapeEl && shapeEl.footer}
        </div>
    )
}

ComponentAsProp.propTypes = {
    id: PropTypes.string,
    element: PropTypes.node,

    elements: PropTypes.arrayOf(PropTypes.node),

    shapeEl: PropTypes.shape({
        header: PropTypes.node,
        footer: PropTypes.node,
    })
}

export default ComponentAsProp;
