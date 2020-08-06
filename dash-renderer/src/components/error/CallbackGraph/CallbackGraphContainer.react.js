import React, {Component, useState, useMemo, useEffect} from 'react';
import PropTypes from 'prop-types';
import {connect, useSelector} from 'react-redux';
import Cytoscape from 'cytoscape';
import CytoscapeComponent from 'react-cytoscapejs';
import Dagre from 'cytoscape-dagre';
import JSONTree from 'react-json-tree';
import {keys, omit, path} from 'ramda';

import {getPath} from '../../../actions/paths';
import {stringifyId} from '../../../actions/dependencies';
import {onError} from '../../../actions';

import './CallbackGraphContainer.css';
import stylesheet from './CallbackGraphContainerStylesheet';
import {
    updateSelectedNode,
    updateChangedProps,
    updateCallback,
} from './CallbackGraphEffects';

Cytoscape.use(Dagre);

/*
 * Generates all the elements (nodes, edeges) for the dependency graph.
 */
function generateElements(graphs, profile) {
    const consumed = [];
    const elements = [];

    function recordNode(id, property) {
        const idStr = stringifyId(id);
        const idType = typeof id === 'object' ? 'wildcard' : 'component';

        const parent = idStr;
        const child = `${idStr}.${property}`;

        if (!consumed.includes(parent)) {
            consumed.push(parent);
            elements.push({
                data: {
                    id: idStr,
                    label: idStr,
                    type: idType,
                },
            });
        }

        if (!consumed.includes(child)) {
            consumed.push(child);
            elements.push({
                data: {
                    id: child,
                    label: property,
                    parent: parent,
                    type: 'property',
                },
            });
        }

        return child;
    }

    function recordEdge(source, target, type) {
        elements.push({
            data: {
                source: source,
                target: target,
                type: type,
            },
        });
    }

    (graphs.callbacks || []).map((callback, i) => {
        const cb = `__dash_callback__.${callback.output}`;
        const cbProfile = profile.callbacks[callback.output] || {};
        const count = cbProfile.count || 0;
        const time = cbProfile.total || 0;

        elements.push({
            data: {
                id: cb,
                label: `callback.${i}`,
                type: 'callback',
                mode: callback.clientside_function ? 'client' : 'server',
                count: count,
                time: count > 0 ? Math.round(time / count) : 0,
                loadingSet: Date.now(),
                errorSet: Date.now(),
            },
        });

        callback.outputs.map(({id, property}) => {
            const node = recordNode(id, property);
            recordEdge(cb, node, 'output');
        });

        callback.inputs.map(({id, property}) => {
            const node = recordNode(id, property);
            recordEdge(node, cb, 'input');
        });

        callback.state.map(({id, property}) => {
            const node = recordNode(id, property);
            recordEdge(node, cb, 'state');
        });
    });

    return elements;
}

function reduceStatus(status) {
    if (keys(status).length === 2) {
        return status.latest;
    }
    return status;
}

function flattenOutputs(res) {
    const outputs = {};
    for (const idStr in res) {
        for (const prop in res[idStr]) {
            outputs[idStr + '.' + prop] = res[idStr][prop];
        }
    }
    return outputs;
}

function flattenInputs(inArray, final) {
    (inArray || []).forEach(inItem => {
        if (Array.isArray(inItem)) {
            flattenInputs(inItem, final);
        } else {
            const {id, property, value} = inItem;
            final[stringifyId(id) + '.' + property] = value;
        }
    });
    return final;
}

// len('__dash_callback__.')
const cbPrefixLen = 18;

function CallbackGraph() {
    // Grab items from the redux store.
    const paths = useSelector(state => state.paths);
    const layout = useSelector(state => state.layout);
    const graphs = useSelector(state => state.graphs);
    const profile = useSelector(state => state.profile);
    const changed = useSelector(state => state.changed);
    const lifecycleState = useSelector(state => state.appLifecycle);

    // Keep track of cytoscape reference and user selected items.
    const [selected, setSelected] = useState(null);
    const [cytoscape, setCytoscape] = useState(null);

    // Generate and memoize the elements.
    const elements = useMemo(() => generateElements(graphs, profile), [graphs]);

    // Custom hook to make sure cytoscape is loaded.
    const useCytoscapeEffect = (effect, condition) => {
        useEffect(
            () => (cytoscape && effect(cytoscape)) || undefined,
            condition
        );
    };

    function setPresetLayout({cy}) {
        const positions = {};
        cy.nodes().each(n => {
            positions[n.id()] = n.position();
        });
        profile.graphLayout = {
            name: 'preset',
            fit: false,
            positions,
            zoom: cy.zoom(),
            pan: cy.pan(),
        };
    }

    // Adds callbacks once cyctoscape is intialized.
    useCytoscapeEffect(
        cy => {
            cytoscape.on('tap', 'node', e => setSelected(e.target));
            cytoscape.on('tap', e => {
                if (e.target === cy) {
                    setSelected(null);
                }
            });
            cytoscape.on('zoom', setPresetLayout);
            cytoscape.on('pan', setPresetLayout);
            cytoscape.nodes().on('position', setPresetLayout);
        },
        [cytoscape]
    );

    // Set node classes on selected.
    useCytoscapeEffect(
        cy => selected && updateSelectedNode(cy, selected.data().id),
        [selected]
    );

    // Flash classes when props change. Uses changed as a trigger. Also
    // flash all input edges originating from this node and highlight
    // the subtree that contains the selected node.
    useCytoscapeEffect(
        cy => changed && updateChangedProps(cy, changed.id, changed.props),
        [changed]
    );

    // Update callbacks from profiling information.
    useCytoscapeEffect(
        cy =>
            profile.updated.forEach(cb =>
                updateCallback(cy, cb, profile.callbacks[cb])
            ),
        [profile.updated]
    );

    if (lifecycleState !== 'HYDRATED') {
        // If we get here too early - most likely during hot reloading - then
        // we need to bail out and wait for the full state to be available
        return (
            <div className="dash-callback-dag--container">
                <div className="dash-callback-dag--message">
                    <div>Waiting for app to be ready...</div>
                </div>
            </div>
        );
    }

    // FIXME: Move to a new component?
    // Generate the element introspection data.
    let elementName = '';
    let elementInfo = {};
    let hasPatterns = false;

    if (selected) {
        function getComponent(id) {
            // for now ignore pattern-matching IDs
            // to do better we may need to store the *actual* IDs used for each
            // callback invocation, since they need not match what's on the page now.
            if (id.charAt(0) === '{') {
                hasPatterns = true;
                return undefined;
            }
            const idPath = getPath(paths, id);
            return idPath ? path(idPath, layout) : undefined;
        }

        function getPropValue(data) {
            const parent = getComponent(data.parent);
            return parent ? parent.props[data.label] : undefined;
        }

        const data = selected.data();

        switch (data.type) {
            case 'component': {
                const rest = omit(['id'], getComponent(data.id)?.props);
                elementInfo = rest;
                elementName = data.id;
                break;
            }

            case 'property': {
                elementName = data.parent;
                elementInfo[data.label] = getPropValue(data);
                break;
            }

            // callback
            default: {
                elementInfo.type = data.mode;

                // Remove uid and set profile.
                const callbackOutputId = data.id.slice(cbPrefixLen);
                elementName = callbackOutputId.replace(/(^\.\.|\.\.$)/g, '');
                const cbProfile = profile.callbacks[callbackOutputId];
                if (cbProfile) {
                    const {
                        count,
                        status,
                        network,
                        resources,
                        total,
                        compute,
                        result,
                        inputs,
                        state,
                    } = cbProfile;
                    elementInfo['call count'] = count;
                    elementInfo.status = reduceStatus(status);
                    const timing = (elementInfo[
                        'timing (total milliseconds)'
                    ] = {
                        total,
                        compute,
                    });
                    if (data.mode === 'server') {
                        timing.network = network.time;
                        elementInfo['data transfer (total bytes)'] = {
                            download: network.download,
                            upload: network.upload,
                        };
                    }
                    for (const key in resources) {
                        timing['user: ' + key] = resources[key];
                    }

                    elementInfo.outputs = flattenOutputs(result);
                    elementInfo.inputs = flattenInputs(inputs, {});
                    elementInfo.state = flattenInputs(state, {});
                } else {
                    elementInfo.callCount = 0;
                }
            }
        }
    }

    const {graphLayout} = profile;
    const cyLayout = graphLayout || {
        name: 'dagre',
        padding: 10,
        spacingFactor: 0.8,
        // after initial layout, just use this again on later draws
        // but we'll also save the layout whenever users interact with it
        ready: setPresetLayout,
    };

    return (
        <div className="dash-callback-dag--container">
            <CytoscapeComponent
                style={{width: '100%', height: '100%'}}
                cy={setCytoscape}
                elements={elements}
                layout={cyLayout}
                stylesheet={stylesheet}
            />
            {selected ? (
                <div className="dash-callback-dag--info">
                    {hasPatterns ? (
                        <div>
                            Info isn't supported for pattern-matching IDs at
                            this time
                        </div>
                    ) : null}
                    <JSONTree
                        data={elementInfo}
                        theme="summerfruit"
                        labelRenderer={keys =>
                            keys.length === 1 ? elementName : keys[0]
                        }
                        getItemString={(type, data, itemType) => (
                            <span>{itemType}</span>
                        )}
                        shouldExpandNode={(keyName, data, level) => level < 1}
                    />
                </div>
            ) : null}
        </div>
    );
}

CallbackGraph.propTypes = {};

class UnconnectedCallbackGraphContainer extends Component {
    constructor(props) {
        super(props);
        this.state = {hasError: false};
    }

    static getDerivedStateFromError(_) {
        return {hasError: true};
    }

    componentDidCatch(error, info) {
        const {dispatch} = this.props;
        dispatch(
            onError({
                myID: this.state.myID,
                type: 'frontEnd',
                error,
                info,
            })
        );
    }

    render() {
        return this.state.hasError ? (
            <div className="dash-callback-dag--container">
                <div className="dash-callback-dag--message">
                    <div>Oops! The callback graph threw an error.</div>
                    <div>Check the error list for details.</div>
                </div>
            </div>
        ) : (
            <CallbackGraph />
        );
    }
}

UnconnectedCallbackGraphContainer.propTypes = {
    dispatch: PropTypes.func,
};

const CallbackGraphContainer = connect(null, dispatch => ({dispatch}))(
    UnconnectedCallbackGraphContainer
);

export {CallbackGraphContainer};
