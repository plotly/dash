'use strict'

import R from 'ramda';
import React from 'react';
import Registry from './registery.js';
import Draggable from './components/core/Draggable.react.js';
import Droppable from './components/core/Droppable.react.js';
import EditableContent from './components/core/EditableContent.react.js';

export default function render(component, path=[]) {


    let content;
    if (!R.has('children', component)) {
        content = [];
    }
    else if (Array.isArray(component.children)) {
        content = component.children.map((v, i) => {
            return render(v, R.append(i, path));
        });
    }
    else if (typeof component.children === 'string') {
        content = [component.children];
    }

    content = React.createElement(
        R.has(component.type, Registry) ? Registry[component.type] : component.type,
        Object.assign({}, component.props, {path}),
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
    if (component.onChange) {
        content = (
            <EditableContent>
                {content}
            </EditableContent>
        );
    }

    return content;

}
