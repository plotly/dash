import React, {Component, useState, useMemo, useEffect, useRef} from 'react';
import PropTypes from 'prop-types';
import {connect, useSelector} from 'react-redux';
import Cytoscape from 'cytoscape';
import CytoscapeComponent from 'react-cytoscapejs';
import dagre from 'cytoscape-dagre';
import fcose from 'cytoscape-fcose';
import {JSONTree} from 'react-json-tree';
import {keys, mergeRight, omit, path, values} from 'ramda';

import {getPath} from '../../../actions/paths';
import {stringifyId} from '../../../actions/dependencies';
import {onError} from '../../../actions';

import './CallbackGraphContainer.css';
import stylesheet from './CallbackGraphContainerStylesheet';
import {
    updateSelectedNode,
    updateChangedProps,
    updateCallback
} from './CallbackGraphEffects';

Cytoscape.use(dagre);
Cytoscape.use(fcose);

/*
 * Generates all the elements (nodes, edges) for the dependency graph.
 */
function generateElements(graphs, profile, extraLinks) {
    const consumed = [];
    const elements = [];
    const structure = {};

    function recordNode(id, rawProperty) {
        const property = rawProperty.split('@')[0];
        const idStr = stringifyId(id);
        const idType = typeof id === 'object' ? 'wildcard' : 'component';

        // dagre layout has problems with eg `width` property - so prepend an X
        const parentId = idStr;
        const childId = `${parentId}.X${property}`;

        if (!consumed.includes(parentId)) {
            consumed.push(parentId);
            elements.push({
                data: {
                    id: parentId,
                    label: idStr,
                    type: idType
                }
            });
            structure[parentId] = [];
        }

        if (!consumed.includes(childId)) {
            consumed.push(childId);
            elements.push({
                data: {
                    id: childId,
                    label: property,
                    parent: parentId,
                    type: 'property'
                }
            });
            structure[parentId].push(childId);
        }

        return childId;
    }

    function recordEdge(source, target, type) {
        elements.push({
            data: {
                source: source,
                target: target,
                type: type
            }
        });
    }

    (graphs.callbacks || []).forEach((callback, i) => {
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
                errorSet: Date.now()
            }
        });

        callback.outputs.map(({id, property}) => {
            const nodeId = recordNode(id, property);
            recordEdge(cb, nodeId, 'output');
        });

        callback.inputs.map(({id, property}) => {
            const nodeId = recordNode(id, property);
            recordEdge(nodeId, cb, 'input');
        });

        callback.state.map(({id, property}) => {
            const nodeId = recordNode(id, property);
            recordEdge(nodeId, cb, 'state');
        });
    });

    // pull together props in the same component
    if (extraLinks) {
        values(structure).forEach(childIds => {
            childIds.forEach(childFrom => {
                childIds.forEach(childTo => {
                    if (childFrom !== childTo) {
                        recordEdge(childFrom, childTo, 'hidden');
                    }
                });
            });
        });
    }

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

function cleanOutputId(outputId) {
    return outputId
        .replace(/(^\.\.|\.\.$)/g, '')
        .split('...')
        .reduce(
            (agg, next) =>
                agg.concat(
                    next.replace(/(.*\..*)(@.+)$/, (a, b) => b + ' (Duplicate)')
                ),
            []
        )
        .join('...');
}

// len('__dash_callback__.')
const cbPrefixLen = 18;

const dagreLayout = {
    name: 'dagre',
    padding: 10,
    ranker: 'tight-tree'
};

const forceLayout = {name: 'fcose', padding: 10, animate: false};

const layouts = {
    'top-down': {...dagreLayout, spacingFactor: 0.8},
    'left-right': {...dagreLayout, nodeSep: 0, rankSep: 80, rankDir: 'LR'},
    force: forceLayout,
    'force-loose': forceLayout
};

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

    const {graphLayout} = profile;
    const chosenType = graphLayout?._chosenType;
    const layoutSelector = useRef(null);
    const [layoutType, setLayoutType] = useState(chosenType || 'top-down');

    // Generate and memoize the elements.
    const elements = useMemo(
        () => generateElements(graphs, profile, layoutType === 'force'),
        [graphs, layoutType]
    );

    // Custom hook to make sure cytoscape is loaded.
    const useCytoscapeEffect = (effect, condition) => {
        useEffect(
            () => (cytoscape && effect(cytoscape)) || undefined,
            condition
        );
    };

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

    function setPresetLayout({cy}) {
        const positions = {};
        cy.nodes().each(n => {
            positions[n.id()] = n.position();
        });

        // Hack! We're mutating the redux store directly here, rather than
        // dispatching an action, because we don't want this to trigger a
        // rerender, we just want the layout to persist when the callback graph
        // is rerendered - either because there's new profile information to
        // display or because the graph was closed and reopened. The latter is
        // the reason we're not using component state to store the layout.
        profile.graphLayout = {
            name: 'preset',
            fit: false,
            positions,
            zoom: cy.zoom(),
            pan: cy.pan(),
            _chosenType: layoutSelector.current?.value
        };
    }

    // Adds callbacks once cyctoscape is initialized.
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
            <div className='dash-callback-dag--container'>
                <div className='dash-callback-dag--message'>
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
                elementName = cleanOutputId(callbackOutputId);
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
                        state
                    } = cbProfile;

                    const avg = v => Math.round(v / (count || 1));

                    elementInfo['call count'] = count;
                    elementInfo.status = reduceStatus(status);

                    const timing = (elementInfo['time (avg milliseconds)'] = {
                        total: avg(total),
                        compute: avg(compute)
                    });
                    if (data.mode === 'server') {
                        timing.network = avg(network.time);

                        elementInfo['data transfer (avg bytes)'] = {
                            download: avg(network.download),
                            upload: avg(network.upload)
                        };
                    }
                    for (const key in resources) {
                        timing['user: ' + key] = avg(resources[key]);
                    }

                    elementInfo.outputs = flattenOutputs(result);
                    elementInfo.inputs = flattenInputs(inputs, {});
                    elementInfo.state = flattenInputs(state, {});
                } else {
                    elementInfo['call count'] = 0;
                }
            }
        }
    }

    const cyLayout =
        chosenType === layoutType
            ? graphLayout
            : mergeRight(layouts[layoutType], {ready: setPresetLayout});

    return (
        <div className='dash-callback-dag--container'>
            <CytoscapeComponent
                style={{width: '100%', height: '100%'}}
                cy={setCytoscape}
                elements={elements}
                layout={cyLayout}
                stylesheet={stylesheet}
            />
            {selected ? (
                <div className='dash-callback-dag--info'>
                    {hasPatterns ? (
                        <div>
                            Info isn't supported for pattern-matching IDs at
                            this time
                        </div>
                    ) : null}
                    <JSONTree
                        data={elementInfo}
                        theme='summerfruit'
                        labelRenderer={_keys =>
                            _keys.length === 1 ? elementName : _keys[0]
                        }
                        getItemString={(type, data, itemType) => (
                            <span>{itemType}</span>
                        )}
                        shouldExpandNode={(keyName, data, level) => level < 1}
                    />
                </div>
            ) : null}
            <select
                className='dash-callback-dag--layoutSelector'
                onChange={e => setLayoutType(e.target.value)}
                value={layoutType}
                ref={layoutSelector}
            >
                {keys(layouts).map(k => (
                    <option value={k} key={k}>
                        {k}
                    </option>
                ))}
            </select>
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
                info
            })
        );
    }

    render() {
        return this.state.hasError ? (
            <div className='dash-callback-dag--container'>
                <div className='dash-callback-dag--message'>
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
    dispatch: PropTypes.func
};

const CallbackGraphContainer = connect(null, dispatch => ({dispatch}))(
    UnconnectedCallbackGraphContainer
);

export {CallbackGraphContainer};
