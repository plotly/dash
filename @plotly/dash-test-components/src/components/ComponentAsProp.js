import React from 'react';
import PropTypes from 'prop-types';


const ComponentAsProp = (props) => {
    const {
        element,
        id,
        shapeEl,
        list_of_shapes,
        multi_components,
        dynamic,
        dynamic_list,
        dynamic_dict,
        dynamic_nested_list,
    } = props;
    return (
        <div id={id}>
            {shapeEl && shapeEl.header}
            {element}
            {shapeEl && shapeEl.footer}
            {list_of_shapes && <ul>{list_of_shapes.map(e => <li key={e.value}>{e.label}</li>)}</ul> }
            {multi_components && <div>{multi_components.map(m => <div id={m.id} key={m.id}>{m.first} - {m.second}</div>)}</div>}
            {
                dynamic && <div>{Object.keys(dynamic).map(key => <div id={key} key={key}>{dynamic[key]}</div>)}</div>
            }
            {
                dynamic_dict && dynamic_dict.node && <div>{Object.keys(dynamic_dict.node).map(key => <div id={key} key={key}>{dynamic_dict.node[key]}</div>)}</div>
            }
            {
                dynamic_list && <div>{dynamic_list.map((obj, i) => Object.keys(obj).map(key => <div id={key} key={key}>{obj[key]}</div>))}</div>
            }
            {
                dynamic_nested_list && <div>{dynamic_nested_list.map((e => <>{Object.values(e.obj)}</>))}</div>
            }
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
    ),

    dynamic: PropTypes.objectOf(PropTypes.node),

    dynamic_list: PropTypes.arrayOf(PropTypes.objectOf(PropTypes.node)),

    dynamic_dict: PropTypes.shape({
        node: PropTypes.objectOf(PropTypes.node),
    }),
    dynamic_nested_list: PropTypes.arrayOf(
        PropTypes.shape({ obj: PropTypes.objectOf(PropTypes.node)})
    ),
}

export default ComponentAsProp;
