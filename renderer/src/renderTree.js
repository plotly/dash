'use strict'

import R from 'ramda';
import React from 'react';
import Registry from './registry';
import Draggable from './components/core/Draggable.react';
import Droppable from './components/core/Droppable.react';
import EditableContent from './components/core/EditableContent.react';
import NotifyObservers from './components/core/NotifyObservers.react';
import {createTreePath} from './reducers/utils';

export default function render(component, dependencyGraph, path=[]) {

    // Create list of child elements
    let children;

    // No children
    if (!R.has('children', component) || !component.children) {
        children = [];
    }
    // Text node child
    else if (typeof component.children === 'string') {
        children = [component.children];
    }
    // One or multiple children
    else {
        const renderChild = (child, i) =>
            render(child, dependencyGraph, R.append(i, path))

        children = (Array.isArray(component.children) ?
                component.children :
                [component.children])
            .map(renderChild);
    }

    // Create wrapping parent element
    const element = R.has(component.type, Registry)
        ? Registry[component.type]
        : component.type; // TODO: check against React's registry - this may not be native component either

    const parent = React.createElement(
        element,
        Object.assign({}, component.props, {path: createTreePath(path)}),
        ...children
    );

    // draggable?
    if (component.draggable) {
        return (
            <Draggable>
                <div> {/* "Only native element nodes can now be passed to React DnD connectors. You can either wrap Header into a <div>, or turn it into a drag source or a drop target itself." */}
                    {parent}
                </div>
            </Draggable>
        );
    }

    // droppable?
    if (component.droppable) {
        return (
            <Droppable>
                {parent}
            </Droppable>
        );
    }

    // editable?
    if (component.props && component.props.editable) {
        return (
            <EditableContent>
                {parent}
            </EditableContent>
        );
    }

    // has observers?
    if (
        component.props &&
        component.props.id &&
        /*
         * in case it isn't initalized yet -
         * TODO: we should be able to remove this check
         * with like a initialization status store or something
         */
        dependencyGraph.hasNode(component.props.id) &&
        dependencyGraph.dependantsOf(component.props.id).length
    ) {
        return (
            <NotifyObservers>
                {parent}
            </NotifyObservers>
        );
    }

    return parent;
}
