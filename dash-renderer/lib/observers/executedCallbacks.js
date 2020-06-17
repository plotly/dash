"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _ramda = require("ramda");

var _callbacks = require("../actions/callbacks");

var _dependencies = require("../actions/dependencies");

var _dependencies_ts = require("../actions/dependencies_ts");

var _actions = require("../actions");

var _paths2 = require("../actions/paths");

var _persistence = require("../persistence");

function ownKeys(object, enumerableOnly) { var keys = Object.keys(object); if (Object.getOwnPropertySymbols) { var symbols = Object.getOwnPropertySymbols(object); if (enumerableOnly) symbols = symbols.filter(function (sym) { return Object.getOwnPropertyDescriptor(object, sym).enumerable; }); keys.push.apply(keys, symbols); } return keys; }

function _objectSpread(target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i] != null ? arguments[i] : {}; if (i % 2) { ownKeys(Object(source), true).forEach(function (key) { _defineProperty(target, key, source[key]); }); } else if (Object.getOwnPropertyDescriptors) { Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)); } else { ownKeys(Object(source)).forEach(function (key) { Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key)); }); } } return target; }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

function _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance"); }

function _iterableToArrayLimit(arr, i) { if (!(Symbol.iterator in Object(arr) || Object.prototype.toString.call(arr) === "[object Arguments]")) { return; } var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

var observer = {
  observer: function observer(_ref) {
    var dispatch = _ref.dispatch,
        getState = _ref.getState;

    var _getState = getState(),
        executed = _getState.callbacks.executed;

    function applyProps(id, updatedProps) {
      var _getState2 = getState(),
          layout = _getState2.layout,
          paths = _getState2.paths;

      var itempath = (0, _paths2.getPath)(paths, id);

      if (!itempath) {
        return false;
      } // This is a callback-generated update.
      // Check if this invalidates existing persisted prop values,
      // or if persistence changed, whether this updates other props.


      updatedProps = (0, _persistence.prunePersistence)((0, _ramda.path)(itempath, layout), updatedProps, dispatch); // In case the update contains whole components, see if any of
      // those components have props to update to persist user edits.

      var _applyPersistence = (0, _persistence.applyPersistence)({
        props: updatedProps
      }, dispatch),
          props = _applyPersistence.props;

      dispatch((0, _actions.updateProps)({
        itempath: itempath,
        props: props,
        source: 'response'
      }));
      return props;
    }

    var requestedCallbacks = [];
    var storedCallbacks = [];
    (0, _ramda.forEach)(function (cb) {
      var _cb$predecessors;

      var predecessors = (0, _ramda.concat)((_cb$predecessors = cb.predecessors) !== null && _cb$predecessors !== void 0 ? _cb$predecessors : [], [cb.callback]);
      var _cb$callback = cb.callback,
          clientside_function = _cb$callback.clientside_function,
          output = _cb$callback.output,
          executionResult = cb.executionResult;

      if ((0, _ramda.isNil)(executionResult)) {
        return;
      }

      var data = executionResult.data,
          error = executionResult.error,
          payload = executionResult.payload;

      if (data !== undefined) {
        (0, _ramda.forEach)(function (_ref2) {
          var _ref3 = _slicedToArray(_ref2, 2),
              id = _ref3[0],
              props = _ref3[1];

          var parsedId = (0, _dependencies.parseIfWildcard)(id);

          var _getState3 = getState(),
              graphs = _getState3.graphs,
              oldLayout = _getState3.layout,
              oldPaths = _getState3.paths; // Components will trigger callbacks on their own as required (eg. derived)


          var appliedProps = applyProps(parsedId, props); // Add callbacks for modified inputs

          requestedCallbacks = (0, _ramda.concat)(requestedCallbacks, (0, _ramda.flatten)((0, _ramda.map)(function (prop) {
            return (0, _dependencies_ts.getCallbacksByInput)(graphs, oldPaths, parsedId, prop, true);
          }, (0, _ramda.keys)(props))).map(function (rcb) {
            return _objectSpread({}, rcb, {
              predecessors: predecessors
            });
          })); // New layout - trigger callbacks for that explicitly

          if ((0, _ramda.has)('children', appliedProps)) {
            var children = appliedProps.children;
            var oldChildrenPath = (0, _ramda.concat)((0, _paths2.getPath)(oldPaths, parsedId), ['props', 'children']);
            var oldChildren = (0, _ramda.path)(oldChildrenPath, oldLayout);
            var paths = (0, _paths2.computePaths)(children, oldChildrenPath, oldPaths);
            dispatch((0, _actions.setPaths)(paths)); // Get callbacks for new layout (w/ execution group)

            requestedCallbacks = (0, _ramda.concat)(requestedCallbacks, (0, _dependencies_ts.getLayoutCallbacks)(graphs, paths, children, {
              chunkPath: oldChildrenPath
            }).map(function (rcb) {
              return _objectSpread({}, rcb, {
                predecessors: predecessors
              });
            })); // Wildcard callbacks with array inputs (ALL / ALLSMALLER) need to trigger
            // even due to the deletion of components

            requestedCallbacks = (0, _ramda.concat)(requestedCallbacks, (0, _dependencies_ts.getLayoutCallbacks)(graphs, oldPaths, oldChildren, {
              removedArrayInputsOnly: true,
              newPaths: paths,
              chunkPath: oldChildrenPath
            }).map(function (rcb) {
              return _objectSpread({}, rcb, {
                predecessors: predecessors
              });
            }));
          } // persistence edge case: if you explicitly update the
          // persistence key, other props may change that require us
          // to fire additional callbacks


          var addedProps = (0, _ramda.pickBy)(function (_, k) {
            return !(k in props);
          }, appliedProps);

          if (!(0, _ramda.isEmpty)(addedProps)) {
            var _getState4 = getState(),
                currentGraphs = _getState4.graphs,
                _paths = _getState4.paths;

            requestedCallbacks = (0, _ramda.concat)(requestedCallbacks, (0, _dependencies_ts.includeObservers)(id, addedProps, currentGraphs, _paths).map(function (rcb) {
              return _objectSpread({}, rcb, {
                predecessors: predecessors
              });
            }));
          }
        }, Object.entries(data)); // Add information about potentially updated outputs vs. updated outputs,
        // this will be used to drop callbacks from execution groups when no output
        // matching the downstream callback's inputs were modified

        storedCallbacks.push(_objectSpread({}, cb, {
          executionMeta: {
            allProps: (0, _ramda.map)(_dependencies_ts.combineIdAndProp, (0, _ramda.flatten)(cb.getOutputs(getState().paths))),
            updatedProps: (0, _ramda.flatten)((0, _ramda.map)(function (_ref4) {
              var _ref5 = _slicedToArray(_ref4, 2),
                  id = _ref5[0],
                  value = _ref5[1];

              return (0, _ramda.map)(function (property) {
                return (0, _dependencies_ts.combineIdAndProp)({
                  id: id,
                  property: property
                });
              }, (0, _ramda.keys)(value));
            }, (0, _ramda.toPairs)(data)))
          }
        }));
      }

      if (error !== undefined) {
        var outputs = payload ? (0, _ramda.map)(_dependencies_ts.combineIdAndProp, (0, _ramda.flatten)([payload.outputs])).join(', ') : output;
        var message = "Callback error updating ".concat(outputs);

        if (clientside_function) {
          var ns = clientside_function.namespace,
              fn = clientside_function.function_name;
          message += " via clientside function ".concat(ns, ".").concat(fn);
        }

        (0, _actions.handleAsyncError)(error, message, dispatch);
        storedCallbacks.push(_objectSpread({}, cb, {
          executionMeta: {
            allProps: (0, _ramda.map)(_dependencies_ts.combineIdAndProp, (0, _ramda.flatten)(cb.getOutputs(getState().paths))),
            updatedProps: []
          }
        }));
      }
    }, executed);
    dispatch((0, _callbacks.aggregateCallbacks)([executed.length ? (0, _callbacks.removeExecutedCallbacks)(executed) : null, executed.length ? (0, _callbacks.addCompletedCallbacks)(executed.length) : null, storedCallbacks.length ? (0, _callbacks.addStoredCallbacks)(storedCallbacks) : null, requestedCallbacks.length ? (0, _callbacks.addRequestedCallbacks)(requestedCallbacks) : null]));
  },
  inputs: ['callbacks.executed']
};
var _default = observer;
exports["default"] = _default;