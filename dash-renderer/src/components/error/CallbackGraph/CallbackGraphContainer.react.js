import React, {Component} from 'react';
import './CallbackGraphContainer.css';

import viz from 'viz.js';

import PropTypes from 'prop-types';

class CallbackGraphContainer extends Component {
    constructor(props) {
        super(props);
    }
    render() {
        const {dependenciesRequest} = this.props;
        const elements = {};
        const callbacks = [];
        const clientside_callbacks = [];
        const links = dependenciesRequest.content.map(({inputs, output, clientside_function}, i) => {
            if (clientside_function) {
                clientside_callbacks.push(`cb${i};`);
            } else {
                callbacks.push(`cb${i};`);
            }
            function recordAndReturn([id, property]) {
                elements[id] = elements[id] || {};
                elements[id][property] = true;
                return `"${id}.${property}"`;
            }
            const out_nodes = output
                .replace(/^\.\./, '')
                .replace(/\.\.$/, '')
                .split('...')
                .map(o => recordAndReturn(o.split('.')))
                .join(', ');
            const in_nodes = inputs
                .map(({id, property}) => recordAndReturn([id, property]))
                .join(', ');
            return `{${in_nodes}} -> cb${i} -> {${out_nodes}};`;
        });

        const dot = `digraph G {
            overlap = false; fontname="Arial"; fontcolor="#333333";
            edge [color="#888888"];
            node [shape=box, fontname="Arial", style=filled, color="#109DFF", fontcolor=white];
            graph [penwidth=0];
            subgraph callbacks {
                node [shape=circle, width=0.3, label="", color="#00CC96"];
                ${callbacks.join('\n')} }

            subgraph clientside_callbacks {
                node [shape=circle, width=0.3, label="", color="#EF553B"];
                ${clientside_callbacks.join('\n')} }

            ${Object.entries(elements)
                .map(
                    ([id, props], i) => `
                subgraph cluster_${i} {
                    bgcolor="#B9C2CE";
                    ${Object.keys(props)
                        .map(p => `"${id}.${p}" [label="${p}"];`)
                        .join('\n')}
                    label = "${id}"; }`
                )
                .join('\n')}

            ${links.join('\n')} }`;

        return (
            <div
                className="dash-callback-dag--container"
                dangerouslySetInnerHTML={{
                    __html: viz(dot, {format: 'svg'}),
                }}
            />
        );
    }
}

CallbackGraphContainer.propTypes = {
    dependenciesRequest: PropTypes.object,
};

export {CallbackGraphContainer};
