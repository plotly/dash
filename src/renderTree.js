'use strict'

import R from 'ramda';
import React, {PropTypes} from 'react';
import Registry from './registry';
import NotifyObservers from './components/core/NotifyObservers.react';


export default function render(component) {
    if (R.contains(R.type(component), ['String', 'Number', 'Null'])) {
        return component;
    }

    // Create list of child elements
    let children;

    const props = R.propOr({}, 'props', component);

    // TODO - Rename component.content to component.children
    if (!R.has('props', component) ||
        !R.has('content', component.props) ||
        typeof component.props.content === 'undefined') {

        // No children
        children = [];

    } else if (R.contains(
        R.type(component.props.content),
        ['String', 'Number', 'Null'])
    ) {

        children = [component.props.content];

    } else {

        // One or multiple objects
        // Recursively render the tree
        // TODO - I think we should pass in `key` here.
        children = (Array.isArray(props.content) ? props.content : [props.content])
                   .map(render);

    }

    const element = Registry.resolve(component.type, component.namespace);
    const parent = React.createElement(
        element,
        R.omit(['content'], component.props),
        ...children
    );

    return (
        <NotifyObservers id={props.id}>
            {parent}
        </NotifyObservers>
    );
}

render.propTypes = {
    content: PropTypes.object,
    id: PropTypes.string
}
