"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _ramda = require("ramda");

var _callbacks = require("../actions/callbacks");

var _dependencies = require("../actions/dependencies");

var _dependencies_ts = require("../actions/dependencies_ts");

var _wait = _interopRequireDefault(require("./../utils/wait"));

var _callbacks2 = require("../utils/callbacks");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

function ownKeys(object, enumerableOnly) { var keys = Object.keys(object); if (Object.getOwnPropertySymbols) { var symbols = Object.getOwnPropertySymbols(object); if (enumerableOnly) symbols = symbols.filter(function (sym) { return Object.getOwnPropertyDescriptor(object, sym).enumerable; }); keys.push.apply(keys, symbols); } return keys; }

function _objectSpread(target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i] != null ? arguments[i] : {}; if (i % 2) { ownKeys(Object(source), true).forEach(function (key) { _defineProperty(target, key, source[key]); }); } else if (Object.getOwnPropertyDescriptors) { Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)); } else { ownKeys(Object(source)).forEach(function (key) { Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key)); }); } } return target; }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function _asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

var observer = {
  observer: function () {
    var _observer = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee(_ref) {
      var dispatch, getState, _getState, callbacks, _getState$callbacks, prioritized, blocked, executing, watched, stored, paths, _getState2, requested, initialRequested, pendingCallbacks, rCirculars, rDuplicates, rMergedDuplicates, pDuplicates, bDuplicates, eDuplicates, wDuplicates, _pruneCallbacks, rAdded, rRemoved, _pruneCallbacks2, pAdded, pRemoved, _pruneCallbacks3, bAdded, bRemoved, _pruneCallbacks4, eAdded, eRemoved, _pruneCallbacks5, wAdded, wRemoved, readyCallbacks, oldBlocked, newBlocked, candidates, _loop, pendingGroups, dropped, added, removed;

      return regeneratorRuntime.wrap(function _callee$(_context) {
        while (1) {
          switch (_context.prev = _context.next) {
            case 0:
              dispatch = _ref.dispatch, getState = _ref.getState;
              _context.next = 3;
              return (0, _wait["default"])(0);

            case 3:
              _getState = getState(), callbacks = _getState.callbacks, _getState$callbacks = _getState.callbacks, prioritized = _getState$callbacks.prioritized, blocked = _getState$callbacks.blocked, executing = _getState$callbacks.executing, watched = _getState$callbacks.watched, stored = _getState$callbacks.stored, paths = _getState.paths;
              _getState2 = getState(), requested = _getState2.callbacks.requested;
              initialRequested = requested.slice(0);
              pendingCallbacks = (0, _callbacks2.getPendingCallbacks)(callbacks);
              /*
                  0. Prune circular callbacks that have completed the loop
                  - cb.callback included in cb.predecessors
              */

              rCirculars = (0, _ramda.filter)(function (cb) {
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

              rDuplicates = [];
              rMergedDuplicates = [];
              (0, _ramda.forEach)(function (group) {
                if (group.length === 1) {
                  // keep callback if its the only one of its kind
                  rMergedDuplicates.push(group[0]);
                } else {
                  var initial = group.find(function (cb) {
                    return cb.initialCall;
                  });

                  if (initial) {
                    // drop the initial callback if it's not alone
                    rDuplicates.push(initial);
                  }

                  var groupWithoutInitial = group.filter(function (cb) {
                    return cb !== initial;
                  });

                  if (groupWithoutInitial.length === 1) {
                    // if there's only one callback beside the initial one, keep that callback
                    rMergedDuplicates.push(groupWithoutInitial[0]);
                  } else {
                    // otherwise merge all remaining callbacks together
                    rDuplicates = (0, _ramda.concat)(rDuplicates, groupWithoutInitial);
                    rMergedDuplicates.push((0, _ramda.mergeLeft)({
                      changedPropIds: (0, _ramda.reduce)((0, _ramda.mergeWith)(Math.max), {}, (0, _ramda.pluck)('changedPropIds', groupWithoutInitial)),
                      executionGroup: (0, _ramda.filter)(function (exg) {
                        return !!exg;
                      }, (0, _ramda.pluck)('executionGroup', groupWithoutInitial)).slice(-1)[0]
                    }, groupWithoutInitial.slice(-1)[0]));
                  }
                }
              }, (0, _ramda.values)((0, _ramda.groupBy)(_dependencies_ts.getUniqueIdentifier, requested)));
              /*
                  TODO?
                  Clean up the `requested` list - during the dispatch phase,
                  duplicates will be removed for real
              */

              requested = rMergedDuplicates;
              /*
                  2. Remove duplicated `prioritized`, `executing` and `watching` callbacks
              */

              /*
                  Extract all but the first callback from each IOS-key group
                  these callbacks are `prioritized` and duplicates.
              */

              pDuplicates = (0, _ramda.flatten)((0, _ramda.map)(function (group) {
                return group.slice(0, -1);
              }, (0, _ramda.values)((0, _ramda.groupBy)(_dependencies_ts.getUniqueIdentifier, (0, _ramda.concat)(prioritized, requested)))));
              bDuplicates = (0, _ramda.flatten)((0, _ramda.map)(function (group) {
                return group.slice(0, -1);
              }, (0, _ramda.values)((0, _ramda.groupBy)(_dependencies_ts.getUniqueIdentifier, (0, _ramda.concat)(blocked, requested)))));
              eDuplicates = (0, _ramda.flatten)((0, _ramda.map)(function (group) {
                return group.slice(0, -1);
              }, (0, _ramda.values)((0, _ramda.groupBy)(_dependencies_ts.getUniqueIdentifier, (0, _ramda.concat)(executing, requested)))));
              wDuplicates = (0, _ramda.flatten)((0, _ramda.map)(function (group) {
                return group.slice(0, -1);
              }, (0, _ramda.values)((0, _ramda.groupBy)(_dependencies_ts.getUniqueIdentifier, (0, _ramda.concat)(watched, requested)))));
              /*
                  3. Modify or remove callbacks that are outputting to non-existing layout `id`.
              */

              _pruneCallbacks = (0, _dependencies_ts.pruneCallbacks)(requested, paths), rAdded = _pruneCallbacks.added, rRemoved = _pruneCallbacks.removed;
              _pruneCallbacks2 = (0, _dependencies_ts.pruneCallbacks)(prioritized, paths), pAdded = _pruneCallbacks2.added, pRemoved = _pruneCallbacks2.removed;
              _pruneCallbacks3 = (0, _dependencies_ts.pruneCallbacks)(blocked, paths), bAdded = _pruneCallbacks3.added, bRemoved = _pruneCallbacks3.removed;
              _pruneCallbacks4 = (0, _dependencies_ts.pruneCallbacks)(executing, paths), eAdded = _pruneCallbacks4.added, eRemoved = _pruneCallbacks4.removed;
              _pruneCallbacks5 = (0, _dependencies_ts.pruneCallbacks)(watched, paths), wAdded = _pruneCallbacks5.added, wRemoved = _pruneCallbacks5.removed;
              /*
                  TODO?
                  Clean up the `requested` list - during the dispatch phase,
                  it will be updated for real
              */

              requested = (0, _ramda.concat)((0, _ramda.difference)(requested, rRemoved), rAdded);
              /*
                  4. Find `requested` callbacks that do not depend on a outstanding output (as either input or state)
              */

              readyCallbacks = (0, _dependencies_ts.getReadyCallbacks)(paths, requested, pendingCallbacks);
              oldBlocked = [];
              newBlocked = [];
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
                candidates = requested.slice(0);

                _loop = function _loop() {
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

                    return _objectSpread(_objectSpread({}, cb), {}, {
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

              pendingGroups = (0, _ramda.groupBy)(function (cb) {
                return cb.executionGroup;
              }, (0, _ramda.filter)(function (cb) {
                return !(0, _ramda.isNil)(cb.executionGroup);
              }, stored));
              dropped = (0, _ramda.filter)(function (cb) {
                // If there is no `stored` callback for the group, no outputs were dropped -> `cb` is kept
                if (!cb.executionGroup || !pendingGroups[cb.executionGroup] || !pendingGroups[cb.executionGroup].length) {
                  return false;
                } // Get all inputs for `cb`


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
              requested = (0, _ramda.difference)(requested, readyCallbacks);
              added = (0, _ramda.difference)(requested, initialRequested);
              removed = (0, _ramda.difference)(initialRequested, requested);
              dispatch((0, _callbacks.aggregateCallbacks)([// Clean up requested callbacks
              added.length ? (0, _callbacks.addRequestedCallbacks)(added) : null, removed.length ? (0, _callbacks.removeRequestedCallbacks)(removed) : null, // Clean up duplicated callbacks
              pDuplicates.length ? (0, _callbacks.removePrioritizedCallbacks)(pDuplicates) : null, bDuplicates.length ? (0, _callbacks.removeBlockedCallbacks)(bDuplicates) : null, eDuplicates.length ? (0, _callbacks.removeExecutingCallbacks)(eDuplicates) : null, wDuplicates.length ? (0, _callbacks.removeWatchedCallbacks)(wDuplicates) : null, // Prune callbacks
              pRemoved.length ? (0, _callbacks.removePrioritizedCallbacks)(pRemoved) : null, pAdded.length ? (0, _callbacks.addPrioritizedCallbacks)(pAdded) : null, bRemoved.length ? (0, _callbacks.removeBlockedCallbacks)(bRemoved) : null, bAdded.length ? (0, _callbacks.addBlockedCallbacks)(bAdded) : null, eRemoved.length ? (0, _callbacks.removeExecutingCallbacks)(eRemoved) : null, eAdded.length ? (0, _callbacks.addExecutingCallbacks)(eAdded) : null, wRemoved.length ? (0, _callbacks.removeWatchedCallbacks)(wRemoved) : null, wAdded.length ? (0, _callbacks.addWatchedCallbacks)(wAdded) : null, // Promote callbacks
              readyCallbacks.length ? (0, _callbacks.addPrioritizedCallbacks)(readyCallbacks) : null]));

            case 36:
            case "end":
              return _context.stop();
          }
        }
      }, _callee);
    }));

    function observer(_x) {
      return _observer.apply(this, arguments);
    }

    return observer;
  }(),
  inputs: ['callbacks.requested', 'callbacks.completed']
};
var _default = observer;
exports["default"] = _default;