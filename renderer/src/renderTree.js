'use strict'

import R from 'ramda';
import React from 'react';
import Registry from './registery.js';
import Draggable from './components/core/Draggable.react.js';
import Droppable from './components/core/Droppable.react.js';
import EditableContent from './components/core/EditableContent.react.js';
import UpdateDependants from './components/core/UpdateDependants.react.js';
import {createTreePath} from './reducers/utils.js';

export default function render(component, dependencyGraph, path=[]) {

    let content;
    if (!R.has('children', component)) {
        content = [];
    }
    else if (Array.isArray(component.children)) {
        content = component.children.map((v, i) => {
            return render(v, dependencyGraph, R.append(i, path));
        });
    }
    else if (typeof component.children === 'string') {
        content = [component.children];
    }

    content = React.createElement(
        R.has(component.type, Registry) ? Registry[component.type] : component.type,
        Object.assign({}, component.props, {path: createTreePath(path)}),
        ...content
    );

    // draggable?
    if (component.draggable) {
        content = (
            <Draggable>
                <div> {/* "Only native element nodes can now be passed to React DnD connectors. You can either wrap Header into a <div>, or turn it into a drag source or a drop target itself." */}
                    {content}
                </div>
            </Draggable>
        );
    }

    // droppable?
    if (component.droppable) {
        content = (
            <Droppable>
                {content}
            </Droppable>
        );
    }

    // editable?
    if (component.props && component.props.editable) {
        content = (
            <EditableContent>
                {content}
            </EditableContent>
        );
    }

    // has dependants?
    if (component.props &&  component.props.id && dependencyGraph.dependantsOf(component.props.id)) {
        content = (
            <UpdateDependants>
                {content}
            </UpdateDependants>
        );
    }

    return content;

}
