"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _ramda = require("ramda");

var _callbacks = require("../actions/callbacks");

var _dependencies = require("../actions/dependencies");

var _dependencies_ts = require("../actions/dependencies_ts");

var _callbacks2 = require("../utils/callbacks");

function ownKeys(object, enumerableOnly) { var keys = Object.keys(object); if (Object.getOwnPropertySymbols) { var symbols = Object.getOwnPropertySymbols(object); if (enumerableOnly) symbols = symbols.filter(function (sym) { return Object.getOwnPropertyDescriptor(object, sym).enumerable; }); keys.push.apply(keys, symbols); } return keys; }

function _objectSpread(target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i] != null ? arguments[i] : {}; if (i % 2) { ownKeys(Object(source), true).forEach(function (key) { _defineProperty(target, key, source[key]); }); } else if (Object.getOwnPropertyDescriptors) { Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)); } else { ownKeys(Object(source)).forEach(function (key) { Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key)); }); } } return target; }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

var observer = {
  observer: function observer(_ref) {
    var dispatch = _ref.dispatch,
        getState = _ref.getState;

    var _getState = getState(),
        callbacks = _getState.callbacks,
        _getState$callbacks = _getState.callbacks,
        prioritized = _getState$callbacks.prioritized,
        blocked = _getState$callbacks.blocked,
        executing = _getState$callbacks.executing,
        watched = _getState$callbacks.watched,
        stored = _getState$callbacks.stored,
        paths = _getState.paths;

    var _getState2 = getState(),
        requested = _getState2.callbacks.requested;

    var pendingCallbacks = (0, _callbacks2.getPendingCallbacks)(callbacks);
    /*
        0. Prune circular callbacks that have completed the loop
        - cb.callback included in cb.predecessors
    */

    var rCirculars = (0, _ramda.filter)(function (cb) {
      var _cb$predecessors;

      return (0, _ramda.includes)(cb.callback, (_cb$predecessors = cb.predecessors) !== null && _cb$predecessors !== void 0 ? _cb$predecessors : []);
    }, requested);
    /*
        TODO?
        Clean up the `requested` list - during the dispatch phase,
        circulars will be removed for real
    */

    requested = (0, _ramda.difference)(requested, rCirculars);
    /*
        1. Remove duplicated `requested` callbacks - give precedence to newer callbacks over older ones
    */

    /*
        Extract all but the first callback from each IOS-key group
        these callbacks are duplicates.
    */

    var rDuplicates = (0, _ramda.flatten)((0, _ramda.map)(function (group) {
      return group.slice(0, -1);
    }, (0, _ramda.values)((0, _ramda.groupBy)(_dependencies_ts.getUniqueIdentifier, requested))));
    /*
        TODO?
        Clean up the `requested` list - during the dispatch phase,
        duplicates will be removed for real
    */

    requested = (0, _ramda.difference)(requested, rDuplicates);
    /*
        2. Remove duplicated `prioritized`, `executing` and `watching` callbacks
    */

    /*
        Extract all but the first callback from each IOS-key group
        these callbacks are `prioritized` and duplicates.
    */

    var pDuplicates = (0, _ramda.flatten)((0, _ramda.map)(function (group) {
      return group.slice(0, -1);
    }, (0, _ramda.values)((0, _ramda.groupBy)(_dependencies_ts.getUniqueIdentifier, (0, _ramda.concat)(prioritized, requested)))));
    var bDuplicates = (0, _ramda.flatten)((0, _ramda.map)(function (group) {
      return group.slice(0, -1);
    }, (0, _ramda.values)((0, _ramda.groupBy)(_dependencies_ts.getUniqueIdentifier, (0, _ramda.concat)(blocked, requested)))));
    var eDuplicates = (0, _ramda.flatten)((0, _ramda.map)(function (group) {
      return group.slice(0, -1);
    }, (0, _ramda.values)((0, _ramda.groupBy)(_dependencies_ts.getUniqueIdentifier, (0, _ramda.concat)(executing, requested)))));
    var wDuplicates = (0, _ramda.flatten)((0, _ramda.map)(function (group) {
      return group.slice(0, -1);
    }, (0, _ramda.values)((0, _ramda.groupBy)(_dependencies_ts.getUniqueIdentifier, (0, _ramda.concat)(watched, requested)))));
    /*
        3. Modify or remove callbacks that are outputing to non-existing layout `id`.
    */

    var _pruneCallbacks = (0, _dependencies_ts.pruneCallbacks)(requested, paths),
        rAdded = _pruneCallbacks.added,
        rRemoved = _pruneCallbacks.removed;

    var _pruneCallbacks2 = (0, _dependencies_ts.pruneCallbacks)(prioritized, paths),
        pAdded = _pruneCallbacks2.added,
        pRemoved = _pruneCallbacks2.removed;

    var _pruneCallbacks3 = (0, _dependencies_ts.pruneCallbacks)(blocked, paths),
        bAdded = _pruneCallbacks3.added,
        bRemoved = _pruneCallbacks3.removed;

    var _pruneCallbacks4 = (0, _dependencies_ts.pruneCallbacks)(executing, paths),
        eAdded = _pruneCallbacks4.added,
        eRemoved = _pruneCallbacks4.removed;

    var _pruneCallbacks5 = (0, _dependencies_ts.pruneCallbacks)(watched, paths),
        wAdded = _pruneCallbacks5.added,
        wRemoved = _pruneCallbacks5.removed;
    /*
        TODO?
        Clean up the `requested` list - during the dispatch phase,
        it will be updated for real
    */


    requested = (0, _ramda.concat)((0, _ramda.difference)(requested, rRemoved), rAdded);
    /*
        4. Find `requested` callbacks that do not depend on a outstanding output (as either input or state)
    */

    var readyCallbacks = (0, _dependencies_ts.getReadyCallbacks)(paths, requested, pendingCallbacks);
    var oldBlocked = [];
    var newBlocked = [];
    /**
     * If there is :
     * - no ready callbacks
     * - at least one requested callback
     * - no additional pending callbacks
     *
     * can assume:
     * - the requested callbacks are part of a circular dependency loop
     *
     * then recursively:
     * - assume the first callback in the list is ready (the entry point for the loop)
     * - check what callbacks are blocked / ready with the assumption
     * - update the missing predecessors based on assumptions
     * - continue until there are no remaining candidates
     *
     */

    if (!readyCallbacks.length && requested.length && requested.length === pendingCallbacks.length) {
      var candidates = requested.slice(0);

      var _loop = function _loop() {
        // Assume 1st callback is ready and
        // update candidates / readyCallbacks accordingly
        var readyCallback = candidates[0];
        readyCallbacks.push(readyCallback);
        candidates = candidates.slice(1); // Remaining candidates are not blocked by current assumptions

        candidates = (0, _dependencies_ts.getReadyCallbacks)(paths, candidates, readyCallbacks); // Blocked requests need to make sure they have the callback as a predecessor

        var blockedByAssumptions = (0, _ramda.difference)(candidates, candidates);
        var modified = (0, _ramda.filter)(function (cb) {
          return !cb.predecessors || !(0, _ramda.includes)(readyCallback.callback, cb.predecessors);
        }, blockedByAssumptions);
        oldBlocked = (0, _ramda.concat)(oldBlocked, modified);
        newBlocked = (0, _ramda.concat)(newBlocked, modified.map(function (cb) {
          var _cb$predecessors2;

          return _objectSpread({}, cb, {
            predecessors: (0, _ramda.concat)((_cb$predecessors2 = cb.predecessors) !== null && _cb$predecessors2 !== void 0 ? _cb$predecessors2 : [], [readyCallback.callback])
          });
        }));
      };

      while (candidates.length) {
        _loop();
      }
    }
    /*
        TODO?
        Clean up the `requested` list - during the dispatch phase,
        it will be updated for real
    */


    requested = (0, _ramda.concat)((0, _ramda.difference)(requested, oldBlocked), newBlocked);
    /*
        5. Prune callbacks that became irrelevant in their `executionGroup`
    */
    // Group by executionGroup, drop non-executionGroup callbacks
    // those were not triggered by layout changes and don't have "strong" interdependency for
    // callback chain completion

    var pendingGroups = (0, _ramda.groupBy)(function (cb) {
      return cb.executionGroup;
    }, (0, _ramda.filter)(function (cb) {
      return !(0, _ramda.isNil)(cb.executionGroup);
    }, stored));
    var dropped = (0, _ramda.filter)(function (cb) {
      // If there is no `stored` callback for the group, no outputs were dropped -> `cb` is kept
      if (!cb.executionGroup || !pendingGroups[cb.executionGroup] || !pendingGroups[cb.executionGroup].length) {
        return false;
      } // Get all intputs for `cb`


      var inputs = (0, _ramda.map)(_dependencies_ts.combineIdAndProp, (0, _ramda.flatten)(cb.getInputs(paths))); // Get all the potentially updated props for the group so far

      var allProps = (0, _ramda.flatten)((0, _ramda.map)(function (gcb) {
        return gcb.executionMeta.allProps;
      }, pendingGroups[cb.executionGroup])); // Get all the updated props for the group so far

      var updated = (0, _ramda.flatten)((0, _ramda.map)(function (gcb) {
        return gcb.executionMeta.updatedProps;
      }, pendingGroups[cb.executionGroup])); // If there's no overlap between the updated props and the inputs,
      // + there's no props that aren't covered by the potentially updated props,
      // and not all inputs are multi valued
      // -> drop `cb`

      var res = (0, _ramda.isEmpty)((0, _ramda.intersection)(inputs, updated)) && (0, _ramda.isEmpty)((0, _ramda.difference)(inputs, allProps)) && !(0, _ramda.all)(_dependencies.isMultiValued, cb.callback.inputs);
      return res;
    }, readyCallbacks);
    /*
        TODO?
        Clean up the `requested` list - during the dispatch phase,
        it will be updated for real
    */

    requested = (0, _ramda.difference)(requested, dropped);
    readyCallbacks = (0, _ramda.difference)(readyCallbacks, dropped);
    dispatch((0, _callbacks.aggregateCallbacks)([// Clean up duplicated callbacks
    rDuplicates.length ? (0, _callbacks.removeRequestedCallbacks)(rDuplicates) : null, pDuplicates.length ? (0, _callbacks.removePrioritizedCallbacks)(pDuplicates) : null, bDuplicates.length ? (0, _callbacks.removeBlockedCallbacks)(bDuplicates) : null, eDuplicates.length ? (0, _callbacks.removeExecutingCallbacks)(eDuplicates) : null, wDuplicates.length ? (0, _callbacks.removeWatchedCallbacks)(wDuplicates) : null, // Prune callbacks
    rRemoved.length ? (0, _callbacks.removeRequestedCallbacks)(rRemoved) : null, rAdded.length ? (0, _callbacks.addRequestedCallbacks)(rAdded) : null, pRemoved.length ? (0, _callbacks.removePrioritizedCallbacks)(pRemoved) : null, pAdded.length ? (0, _callbacks.addPrioritizedCallbacks)(pAdded) : null, bRemoved.length ? (0, _callbacks.removeBlockedCallbacks)(bRemoved) : null, bAdded.length ? (0, _callbacks.addBlockedCallbacks)(bAdded) : null, eRemoved.length ? (0, _callbacks.removeExecutingCallbacks)(eRemoved) : null, eAdded.length ? (0, _callbacks.addExecutingCallbacks)(eAdded) : null, wRemoved.length ? (0, _callbacks.removeWatchedCallbacks)(wRemoved) : null, wAdded.length ? (0, _callbacks.addWatchedCallbacks)(wAdded) : null, // Prune circular callbacks
    rCirculars.length ? (0, _callbacks.removeRequestedCallbacks)(rCirculars) : null, // Prune circular assumptions
    oldBlocked.length ? (0, _callbacks.removeRequestedCallbacks)(oldBlocked) : null, newBlocked.length ? (0, _callbacks.addRequestedCallbacks)(newBlocked) : null, // Drop non-triggered initial callbacks
    dropped.length ? (0, _callbacks.removeRequestedCallbacks)(dropped) : null, // Promote callbacks
    readyCallbacks.length ? (0, _callbacks.removeRequestedCallbacks)(readyCallbacks) : null, readyCallbacks.length ? (0, _callbacks.addPrioritizedCallbacks)(readyCallbacks) : null]));
  },
  inputs: ['callbacks.requested', 'callbacks.completed']
};
var _default = observer;
exports["default"] = _default;