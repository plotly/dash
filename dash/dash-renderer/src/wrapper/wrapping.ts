import React from 'react';
import {mergeRight, type, has} from 'ramda';

export function createElement(
    element: any,
    props: any,
    extraProps: any,
    children: any
) {
    const allProps = mergeRight(props, extraProps);
    if (Array.isArray(children)) {
        return React.createElement(element, allProps, ...children);
    }
    return React.createElement(element, allProps, children);
}

export function isDryComponent(obj: any) {
    return (
        type(obj) === 'Object' &&
        has('type', obj) &&
        has('namespace', obj) &&
        has('props', obj)
    );
}

export function validateComponent(componentDefinition: any) {
    if (type(componentDefinition) === 'Array') {
        throw new Error(
            'The children property of a component is a list of lists, instead ' +
                'of just a list. This can sometimes be due to a trailing comma. ' +
                'Check the component that has the following contents ' +
                'and remove one of the levels of nesting: \n' +
                JSON.stringify(componentDefinition, null, 2)
        );
    }
    if (
        type(componentDefinition) === 'Object' &&
        !(
            has('namespace', componentDefinition) &&
            has('type', componentDefinition) &&
            has('props', componentDefinition)
        )
    ) {
        throw new Error(
            'An object was provided as `children` instead of a component, ' +
                'string, or number (or list of those). ' +
                'Check the children property that looks something like:\n' +
                JSON.stringify(componentDefinition, null, 2)
        );
    }
}
