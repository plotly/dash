import React from 'react';
import PropTypes from 'prop-types';


const ComponentAsProp = (props) => {
    const { element, id, shapeEl, list_of_shapes } = props;
    return (
        <div id={id}>
            {shapeEl && shapeEl.header}
            {element}
            {shapeEl && shapeEl.footer}
            {list_of_shapes && <ul>{list_of_shapes.map(e => <li key={e.value}>{e.label}</li>)}</ul> }
        </div>
    )
}

ComponentAsProp.propTypes = {
    id: PropTypes.string,
    element: PropTypes.node,

    shapeEl: PropTypes.shape({
        header: PropTypes.node,
        footer: PropTypes.node,
    }),

    list_of_shapes: PropTypes.arrayOf(
        PropTypes.exact({
            label: PropTypes.node,
            value: PropTypes.number,
        })
    )
}

export default ComponentAsProp;
