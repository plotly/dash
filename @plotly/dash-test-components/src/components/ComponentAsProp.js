import React from 'react';
import PropTypes from 'prop-types';


const ComponentAsProp = (props) => {
    const { element, id, shapeEl, list_of_shapes, multi_components } = props;
    return (
        <div id={id}>
            {shapeEl && shapeEl.header}
            {element}
            {shapeEl && shapeEl.footer}
            {list_of_shapes && <ul>{list_of_shapes.map(e => <li key={e.value}>{e.label}</li>)}</ul> }
            {multi_components && <div>{multi_components.map(m => <div id={m.id} key={m.id}>{m.first} - {m.second}</div>)}</div>}
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
    ),

    multi_components: PropTypes.arrayOf(
        PropTypes.exact({
            id: PropTypes.string,
            first: PropTypes.node,
            second: PropTypes.node,
        })
    )
}

export default ComponentAsProp;
