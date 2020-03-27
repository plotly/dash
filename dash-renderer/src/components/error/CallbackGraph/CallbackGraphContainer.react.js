import React, {useEffect, useRef} from 'react';
import PropTypes from 'prop-types';

import './CallbackGraphContainer.css';

import Viz from 'viz.js';
import {Module, render} from 'viz.js/full.render';

import {stringifyId} from '../../../actions/dependencies';

const CallbackGraphContainer = ({graphs}) => {
    const el = useRef(null);

    const viz = useRef(null);

    const makeViz = () => {
        viz.current = new Viz({Module, render});
    };

    if (!viz.current) {
        makeViz();
    }

    useEffect(() => {
        const {callbacks} = graphs;
        const elements = {};
        const callbacksOut = [];
        const links = callbacks.map(({inputs, outputs}, i) => {
            callbacksOut.push(`cb${i};`);
            function recordAndReturn({id, property}) {
                const idClean = stringifyId(id)
                    .replace(/[\{\}".;\[\]()]/g, '')
                    .replace(/:/g, '-')
                    .replace(/,/g, '_');
                elements[idClean] = elements[idClean] || {};
                elements[idClean][property] = true;
                return `"${idClean}.${property}"`;
            }
            const out_nodes = outputs.map(recordAndReturn).join(', ');
            const in_nodes = inputs.map(recordAndReturn).join(', ');
            return `{${in_nodes}} -> cb${i} -> {${out_nodes}};`;
        });

        const dot = `digraph G {
            overlap = false; fontname="Arial"; fontcolor="#333333";
            edge [color="#888888"];
            node [shape=box, fontname="Arial", style=filled, color="#109DFF", fontcolor=white];
            graph [penwidth=0];
            subgraph callbacks {
                node [shape=circle, width=0.3, label="", color="#00CC96"];
                ${callbacksOut.join('\n')} }

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

        // eslint-disable-next-line no-console
        console.log(dot);

        viz.current
            .renderSVGElement(dot)
            .then(vizEl => {
                el.current.innerHTML = '';
                el.current.appendChild(vizEl);
            })
            .catch(e => {
                // https://github.com/mdaines/viz.js/wiki/Caveats
                makeViz();
                // eslint-disable-next-line no-console
                console.error(e);
                el.current.innerHTML = 'Error creating callback graph';
            });
    });

    return <div className="dash-callback-dag--container" ref={el} />;
};

CallbackGraphContainer.propTypes = {
    graphs: PropTypes.object,
};

export {CallbackGraphContainer};
