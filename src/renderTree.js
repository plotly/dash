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

    if (!R.has('props', component) ||
        !R.has('children', component.props) ||
        typeof component.props.children === 'undefined') {

        // No children
        children = [];

    } else if (R.contains(
        R.type(component.props.children),
        ['String', 'Number', 'Null'])
    ) {

        children = [component.props.children];

    } else {

        // One or multiple objects
        // Recursively render the tree
        // TODO - I think we should pass in `key` here.
        children = (Array.isArray(props.children) ? props.children : [props.children])
                   .map(render);

    }

    if (!component.type) {
        /* eslint-disable no-console */
        console.error(R.type(component), component);
        /* eslint-enable no-console */
        throw new Error('component.type is undefined');
    }
    if (!component.namespace) {
        /* eslint-disable no-console */
        console.error(R.type(component), component);
        /* eslint-enable no-console */
        throw new Error('component.namespace is undefined');
    }
    const element = Registry.resolve(component.type, component.namespace);

    const parent = React.createElement(
        element,
        R.omit(['children'], component.props),
        ...children
    );

    return (
        <NotifyObservers id={props.id}>
            {parent}
        </NotifyObservers>
    );
}

render.propTypes = {
    children: PropTypes.object,
    id: PropTypes.string
}
