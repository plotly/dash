import React, {Component} from 'react';
import './CallbackGraphContainer.css';

import Viz from 'viz.js';
import {Module, render} from 'viz.js/full.render';

import PropTypes from 'prop-types';

class CallbackGraphContainer extends Component {
    constructor(props) {
        super(props);

        this.viz = null;
        this.updateViz = this.updateViz.bind(this);
    }

    componentDidMount() {
        this.updateViz();
    }

    componentDidUpdate() {
        this.updateViz();
    }

    render() {
        return <div className="dash-callback-dag--container" ref="el" />;
    }

    updateViz() {
        this.viz = this.viz || new Viz({Module, render});

        const {dependenciesRequest} = this.props;
        const elements = {};
        const callbacks = [];
        const links = dependenciesRequest.content.map(({inputs, output}, i) => {
            callbacks.push(`cb${i};`);
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

        const el = this.refs.el;

        this.viz
            .renderSVGElement(dot)
            .then(vizEl => {
                el.innerHTML = '';
                el.appendChild(vizEl);
            })
            .catch(e => {
                // https://github.com/mdaines/viz.js/wiki/Caveats
                this.viz = new Viz({Module, render});
                // eslint-disable-next-line no-console
                console.error(e);
                el.innerHTML = 'Error creating callback graph';
            });
    }
}

CallbackGraphContainer.propTypes = {
    dependenciesRequest: PropTypes.object,
};

export {CallbackGraphContainer};
