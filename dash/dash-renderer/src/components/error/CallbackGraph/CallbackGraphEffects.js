import {STATUS, STATUSMAP} from '../../../constants/constants';

/**
 * getEdgeTypes
 *
 * Finds all edges connected to a node and splits them by type.
 *
 * @param {Object} node - Cytoscape node.
 * @returns {Object} - Object containing the edges, sorted by type.
 */
function getEdgeTypes(node) {
    const elements = node.connectedEdges();
    return {
        input: elements.filter('[type = "input"]'),
        state: elements.filter('[type = "state"]'),
        output: elements.filter('[type = "output"]')
    };
}

/**
 * updateSelected
 *
 * Updates the classes of the selected node and recenters the viewport.
 *
 * @param {Object} cy - Reference to the cytoscape instance.
 * @param {String} id - The id of the selected node.
 * @returns {function} - cleanup function, for useEffect hook
 */
export function updateSelectedNode(cy, id) {
    function ascend(node, collection) {
        // FIXME: Should we include State parents but non-recursively?
        const type = node.data().type === 'callback' ? 'input' : 'output';
        const edges = getEdgeTypes(node)[type];
        const parents = edges.sources();
        collection.merge(edges);
        collection.merge(parents);
        if (node.data().type === 'property') {
            collection.merge(node.ancestors());
        }
        parents.forEach(node => ascend(node, collection));
    }

    function descend(node, collection) {
        const type = node.data().type === 'callback' ? 'output' : 'input';
        const edges = getEdgeTypes(node)[type];
        const children = edges.targets();
        collection.merge(edges);
        collection.merge(children);
        if (node.data().type === 'property') {
            collection.merge(node.ancestors());
        }
        children.forEach(node => descend(node, collection));
    }

    if (id) {
        const node = cy.getElementById(id);

        // Highlight the selected node.

        node.addClass('selected-node');

        // Find the subtree that the node belongs to. A subtree contains
        // all all ancestors and descendants that are connected via Inputs
        // or Outputs (but not State).

        // WARNING: No cycle detection!

        const subtree = cy.collection();
        subtree.merge(node);
        ascend(node, subtree);
        descend(node, subtree);

        const other = subtree.absoluteComplement();
        other.addClass('inactive');

        return () => {
            node.removeClass('selected-node');
            other.removeClass('inactive');
        };
    }
    return undefined;
}

/**
 * updateChangedProp
 *
 * Flashes property nodes that updated and any inputs they are connected to.
 *
 * @param {Object} cy - Reference to the cytoscape instance.
 * @param {String} id - The component id which updated.
 * @param {Object} props - The props that updated.
 * @param {Number} flashTime - The time to flash classes for in ms.
 * @returns {undefined}
 */
export function updateChangedProps(cy, id, props, flashTime = 500) {
    Object.keys(props).forEach(prop => {
        const node = cy.getElementById(`${id}.${prop}`);
        node.flashClass('prop-changed', flashTime);
        node.edgesTo('*')
            .filter('[type = "input"]')
            .flashClass('triggered', flashTime);
    });
}

/**
 * updateCallback
 *
 * Updates a callback node with profiling information (call count, avg time)
 * and adds or removes classes as necessary. Classes are always assert for
 * at least flashTime ms so that they can be visually observed. When callbacks
 * resolve, all output edges are flashed.
 *
 * @param {Object} cy - Reference to the cytoscape instance.
 * @param {String} id - The id of the callback (i.e., it's output identifier)
 * @param {Object} profile - The callback profiling information.
 * @param {Number} flashTime - The time to flash classes for in ms.
 * @returns {undefined}
 */
export function updateCallback(cy, id, profile, flashTime = 500) {
    const node = cy.getElementById(`__dash_callback__.${id}`);
    const {count, total, status} = profile;
    const {latest} = status;

    // Update data.
    const avgTime = count > 0 ? total / count : 0;
    node.data('count', count);
    node.data('time', Math.round(avgTime));

    // Either flash the classes OR maintain it for long callbacks.
    if (latest === 'loading') {
        node.data('loadingSet', Date.now());
        node.addClass('callback-loading');
    } else if (node.hasClass('callback-loading')) {
        const timeLeft = node.data('loadingSet') + flashTime - Date.now();
        setTimeout(
            () => node.removeClass('callback-loading'),
            Math.max(timeLeft, 0)
        );
    }

    if (
        latest !== 'loading' &&
        latest !== STATUSMAP[STATUS.OK] &&
        latest !== STATUSMAP[STATUS.PREVENT_UPDATE]
    ) {
        node.data('errorSet', Date.now());
        node.addClass('callback-error');
    } else if (node.hasClass('callback-error')) {
        const timeLeft = node.data('errorSet') + flashTime - Date.now();
        setTimeout(
            () => node.removeClass('callback-error'),
            Math.max(timeLeft, 0)
        );
    }

    // FIXME: This will flash branches that return no_update!!
    // If the callback resolved properly, flash the outputs.
    if (latest === STATUSMAP[STATUS.OK]) {
        node.edgesTo('*').flashClass('triggered', flashTime);
    }
}
