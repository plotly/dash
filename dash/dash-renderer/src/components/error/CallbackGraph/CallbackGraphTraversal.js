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

export function ascend(
    node,
    collection,
    include_components = false,
    include_edges = false
) {
    // FIXME: Should we include State parents but non-recursively?

    if (
        node.data().type === 'component' &&
        node.isParent() &&
        include_components
    ) {
        collection.merge(node);
    }

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

export function descend(
    node,
    collection,
    include_components = false,
    include_edges = false
) {
    if (
        node.data().type === 'component' &&
        node.isParent() &&
        include_components
    ) {
        collection.merge(node);
    }

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
