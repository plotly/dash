import {STATUS, STATUSMAP} from '../../../constants/constants';

import {ascend, descend} from './CallbackGraphTraversal';
import {layouts} from './CallbackGraphLayouts';

import {mergeRight} from 'ramda';

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
export function updateCallback(
    cy,
    id,
    profile,
    flashTime = 500,
    hideZeroOnly = false,
    layoutType = 'top-down'
) {
    const node = cy.getElementById(`__dash_callback__.${id}`);
    const {count, total, status} = profile;
    const {latest} = status;

    // Update data.
    const avgTime = count > 0 ? total / count : 0;
    node.data('count', count);
    node.data('time', Math.round(avgTime));

    let isProcessing = null;

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

    if (hideZeroOnly) {
        isProcessing = setTimeout(() => {
            const nonZeroNodes = cy
                .nodes()
                .filter(
                    element =>
                        element.data('count') !== undefined &&
                        element.data('count') > 0
                );

            const nonZeroSubtree = cy.collection();
            nonZeroSubtree.merge(nonZeroNodes);
            nonZeroNodes.forEach(nonZeroNode => {
                ascend(nonZeroNode, nonZeroSubtree);
                descend(nonZeroNode, nonZeroSubtree);
            });

            const fitLayout = mergeRight(layouts[layoutType], {fit: true});
            nonZeroSubtree.layout(fitLayout).run();

            nonZeroSubtree.removeClass('hide').addClass('show');

            isProcessing = null;
        }, 1000);
    }

    return isProcessing;
}

export function hideZeroCountNodes(cy, hideZeroOnly, layoutType = 'top-down') {
    if (hideZeroOnly) {
        const zeroNodes = cy
            .nodes()
            .filter(
                element =>
                    element.data('count') === undefined ||
                    element.data('count') == 0
            );

        const zeroEleSubtree = cy.collection();
        zeroEleSubtree.merge(zeroNodes);
        zeroNodes.forEach(zeroNode => {
            ascend(zeroNode, zeroEleSubtree);
            descend(zeroNode, zeroEleSubtree);
        });

        zeroEleSubtree.addClass('hide').removeClass('show');

        const nonZeroNodes = cy
            .nodes()
            .filter(
                element =>
                    element.data('count') !== undefined &&
                    element.data('count') > 0
            );

        const nonZeroEleSubtree = cy.collection();
        nonZeroEleSubtree.merge(nonZeroNodes);
        nonZeroNodes.forEach(nonZeroNode => {
            ascend(nonZeroNode, nonZeroEleSubtree);
            descend(nonZeroNode, nonZeroEleSubtree);
        });

        nonZeroEleSubtree.removeClass('hide').addClass('show');

        setTimeout(() => {
            const fitLayout = mergeRight(layouts[layoutType], {fit: true});
            nonZeroEleSubtree.layout(fitLayout).run();
        }, 1000);
    } else {
        cy.elements()
            .filter(() => true)
            .removeClass('hide');

        setTimeout(() => {
            const fitLayout = mergeRight(layouts[layoutType], {fit: true});
            cy.layout(fitLayout).run();
        }, 1000);
    }
}

export function focusOnSearchItem(cy, nodeId) {
    if (nodeId) {
        const node = cy.getElementById(nodeId);

        const subtree = cy.collection();
        subtree.merge(node);
        ascend(node, subtree);
        descend(node, subtree);

        cy.fit(subtree, 100);

        node.flashClass('found', 1000);
    }
    return undefined;
}
