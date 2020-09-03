"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.updateSelectedNode = updateSelectedNode;
exports.updateChangedProps = updateChangedProps;
exports.updateCallback = updateCallback;

var _constants = require("../../../constants/constants");

/**
 * getEdgeTypes
 *
 * Finds all edges connected to a node and splits them by type.
 *
 * @param {Object} node - Cytoscape node.
 * @returns {Object} - Object contaiing the edges, sorted by type.
 */
function getEdgeTypes(node) {
  var elements = node.connectedEdges();
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


function updateSelectedNode(cy, id) {
  if (id) {
    // Find the subtree that the node belongs to. A subtree contains
    // all all ancestors and descendents that are connected via Inputs
    // or Outputs (but not State).
    // WARNING: No cycle detection!
    var ascend = function ascend(node, collection) {
      // FIXME: Should we include State parents but non-recursively?
      var type = node.data().type === 'callback' ? 'input' : 'output';
      var edges = getEdgeTypes(node)[type];
      var parents = edges.sources();
      collection.merge(edges);
      collection.merge(parents);

      if (node.data().type === 'property') {
        collection.merge(node.ancestors());
      }

      parents.forEach(function (node) {
        return ascend(node, collection);
      });
    };

    var descend = function descend(node, collection) {
      var type = node.data().type === 'callback' ? 'output' : 'input';
      var edges = getEdgeTypes(node)[type];
      var children = edges.targets();
      collection.merge(edges);
      collection.merge(children);

      if (node.data().type === 'property') {
        collection.merge(node.ancestors());
      }

      children.forEach(function (node) {
        return descend(node, collection);
      });
    };

    var node = cy.getElementById(id); // Highlght the selected node.

    node.addClass('selected-node');
    var subtree = cy.collection();
    subtree.merge(node);
    ascend(node, subtree);
    descend(node, subtree);
    var other = subtree.absoluteComplement();
    other.addClass('inactive');
    return function () {
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


function updateChangedProps(cy, id, props) {
  var flashTime = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : 500;
  Object.keys(props).forEach(function (prop) {
    var node = cy.getElementById("".concat(id, ".").concat(prop));
    node.flashClass('prop-changed', flashTime);
    node.edgesTo('*').filter('[type = "input"]').flashClass('triggered', flashTime);
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
 * @param {Object} profile - The callback profiling infomration.
 * @param {Number} flashTime - The time to flash classes for in ms.
 * @returns {undefined}
 */


function updateCallback(cy, id, profile) {
  var flashTime = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : 500;
  var node = cy.getElementById("__dash_callback__.".concat(id));
  var count = profile.count,
      total = profile.total,
      status = profile.status;
  var latest = status.latest; // Update data.

  var avgTime = count > 0 ? total / count : 0;
  node.data('count', count);
  node.data('time', Math.round(avgTime)); // Either flash the classes OR maintain it for long callbacks.

  if (latest === 'loading') {
    node.data('loadingSet', Date.now());
    node.addClass('callback-loading');
  } else if (node.hasClass('callback-loading')) {
    var timeLeft = node.data('loadingSet') + flashTime - Date.now();
    setTimeout(function () {
      return node.removeClass('callback-loading');
    }, Math.max(timeLeft, 0));
  }

  if (latest !== 'loading' && latest !== _constants.STATUSMAP[_constants.STATUS.OK] && latest !== _constants.STATUSMAP[_constants.STATUS.PREVENT_UPDATE]) {
    node.data('errorSet', Date.now());
    node.addClass('callback-error');
  } else if (node.hasClass('callback-error')) {
    var _timeLeft = node.data('errorSet') + flashTime - Date.now();

    setTimeout(function () {
      return node.removeClass('callback-error');
    }, Math.max(_timeLeft, 0));
  } // FIXME: This will flash branches that return no_update!!
  // If the callback resolved properly, flash the outputs.


  if (latest === _constants.STATUSMAP[_constants.STATUS.OK]) {
    node.edgesTo('*').flashClass('triggered', flashTime);
  }
}