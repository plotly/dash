import React, {Component, useState, useMemo, useEffect} from 'react';
import PropTypes from 'prop-types';
import {connect, useSelector} from 'react-redux';
import CytoscapeComponent from 'react-cytoscapejs';
import JSONTree from 'react-json-tree';
import {keys, omit, path} from 'ramda';

import {getPath} from '../../../actions/paths';
import {stringifyId} from '../../../actions/dependencies';
import {onError} from '../../../actions';

import './CallbackGraphContainer.css';
import stylesheet from './CallbackGraphContainerStylesheet';
import {
    getEdgeTypes,
    updateSelectedNode,
    updateChangedProps,
    updateCallback,
} from './CallbackGraphEffects';

// Set the layout method.
// NOTE: dagre should be nicer for DAG, but even with manual
//       cycle pruning, it gives terrible results with State.
const cyLayout = {
    name: 'breadthfirst',
    directed: true,
    padding: 20,
    grid: true,
    spacingFactor: 0.5,
};

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

    // Adds callbacks once cyctoscape is intialized.
    useCytoscapeEffect(
        cy => {
            cytoscape.on('tap', 'node', e => setSelected(e.target));
            cytoscape.on('tap', e => {
                if (e.target === cy) {
                    setSelected(null);
                }
            });
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

        function reduceStatus(status) {
            if (keys(status).length === 2) {
                return status.latest;
            }
            return status;
        }

        function reduceProps(idProps) {
            return idProps.reduce((o, e) => ({
                ...o,
                [e.data().id]: getPropValue(e.data()),
            }), {});
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
                    const {count, status, network, resources, total, compute} = cbProfile;
                    elementInfo['call count'] = count;
                    elementInfo.status = reduceStatus(status);
                    const timing = elementInfo['timing (total milliseconds)'] = {
                        total,
                        compute,
                    };
                    if (data.mode === 'server') {
                        timing.network = network.time;
                        elementInfo['data transfer (total bytes)'] = {
                            download: network.download,
                            upload: network.upload,
                        }
                    }
                    for (const key in resources) {
                        timing['user: ' + key] = resources[key];
                    }
                } else {
                    elementInfo.callCount = 0;
                }

                const edges = getEdgeTypes(selected);
                elementInfo.outputs = reduceProps(edges.output.targets());
                elementInfo.inputs = reduceProps(edges.input.sources());
                elementInfo.states = reduceProps(edges.state.sources());
            }
        }
    }

    return (
        <div className="dash-callback-dag--container">
            <CytoscapeComponent
                style={{width: '100%', height: '100%'}}
                cy={setCytoscape}
                elements={elements}
                layout={window.layout || cyLayout}
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
