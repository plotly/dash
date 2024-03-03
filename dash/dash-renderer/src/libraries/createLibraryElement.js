import {mergeRight} from 'ramda';
import React from 'react';

export function createLibraryElement(element, props, extraProps, children) {
    const allProps = mergeRight(props, extraProps);
    if (Array.isArray(children)) {
        return React.createElement(element, allProps, ...children);
    }
    return React.createElement(element, allProps, children);
}
