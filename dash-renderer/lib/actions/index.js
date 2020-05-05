"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.hydrateInitialOutputs = hydrateInitialOutputs;
exports.getCSRFHeader = getCSRFHeader;
exports.notifyObservers = notifyObservers;
exports.handleAsyncError = handleAsyncError;
exports.revert = exports.undo = exports.redo = exports.dispatchError = exports.onError = exports.setLayout = exports.setHooks = exports.setConfig = exports.setAppLifecycle = exports.setPaths = exports.setGraphs = exports.setRequestQueue = exports.setPendingCallbacks = exports.updateProps = void 0;

var _ramda = require("ramda");

var _reduxActions = require("redux-actions");

var _constants = require("../reducers/constants");

var _constants2 = require("./constants");

var _cookie = _interopRequireDefault(require("cookie"));

var _utils = require("./utils");

var _dependencies = require("./dependencies");

var _paths2 = require("./paths");

var _constants3 = require("../constants/constants");

var _persistence = require("../persistence");

var _isAppReady = _interopRequireDefault(require("./isAppReady"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

function _toConsumableArray(arr) { return _arrayWithoutHoles(arr) || _iterableToArray(arr) || _nonIterableSpread(); }

function _nonIterableSpread() { throw new TypeError("Invalid attempt to spread non-iterable instance"); }

function _iterableToArray(iter) { if (Symbol.iterator in Object(iter) || Object.prototype.toString.call(iter) === "[object Arguments]") return Array.from(iter); }

function _arrayWithoutHoles(arr) { if (Array.isArray(arr)) { for (var i = 0, arr2 = new Array(arr.length); i < arr.length; i++) { arr2[i] = arr[i]; } return arr2; } }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

function _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance"); }

function _iterableToArrayLimit(arr, i) { if (!(Symbol.iterator in Object(arr) || Object.prototype.toString.call(arr) === "[object Arguments]")) { return; } var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function _asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

var updateProps = (0, _reduxActions.createAction)((0, _constants2.getAction)('ON_PROP_CHANGE'));
exports.updateProps = updateProps;
var setPendingCallbacks = (0, _reduxActions.createAction)('SET_PENDING_CALLBACKS');
exports.setPendingCallbacks = setPendingCallbacks;
var setRequestQueue = (0, _reduxActions.createAction)((0, _constants2.getAction)('SET_REQUEST_QUEUE'));
exports.setRequestQueue = setRequestQueue;
var setGraphs = (0, _reduxActions.createAction)((0, _constants2.getAction)('SET_GRAPHS'));
exports.setGraphs = setGraphs;
var setPaths = (0, _reduxActions.createAction)((0, _constants2.getAction)('SET_PATHS'));
exports.setPaths = setPaths;
var setAppLifecycle = (0, _reduxActions.createAction)((0, _constants2.getAction)('SET_APP_LIFECYCLE'));
exports.setAppLifecycle = setAppLifecycle;
var setConfig = (0, _reduxActions.createAction)((0, _constants2.getAction)('SET_CONFIG'));
exports.setConfig = setConfig;
var setHooks = (0, _reduxActions.createAction)((0, _constants2.getAction)('SET_HOOKS'));
exports.setHooks = setHooks;
var setLayout = (0, _reduxActions.createAction)((0, _constants2.getAction)('SET_LAYOUT'));
exports.setLayout = setLayout;
var onError = (0, _reduxActions.createAction)((0, _constants2.getAction)('ON_ERROR'));
exports.onError = onError;

var dispatchError = function dispatchError(dispatch) {
  return function (message, lines) {
    return dispatch(onError({
      type: 'backEnd',
      error: {
        message: message,
        html: lines.join('\n')
      }
    }));
  };
};

exports.dispatchError = dispatchError;

function hydrateInitialOutputs() {
  return function (dispatch, getState) {
    (0, _dependencies.validateCallbacksToLayout)(getState(), dispatchError(dispatch));
    triggerDefaultState(dispatch, getState);
    dispatch(setAppLifecycle((0, _constants.getAppState)('HYDRATED')));
  };
}
/* eslint-disable-next-line no-console */


var logWarningOnce = (0, _ramda.once)(console.warn);

function getCSRFHeader() {
  try {
    return {
      'X-CSRFToken': _cookie["default"].parse(document.cookie)._csrf_token
    };
  } catch (e) {
    logWarningOnce(e);
    return {};
  }
}

function triggerDefaultState(dispatch, getState) {
  var _getState = getState(),
      graphs = _getState.graphs,
      paths = _getState.paths,
      layout = _getState.layout; // overallOrder will assert circular dependencies for multi output.


  try {
    graphs.MultiGraph.overallOrder();
  } catch (err) {
    dispatch(onError({
      type: 'backEnd',
      error: {
        message: 'Circular Dependencies',
        html: err.toString()
      }
    }));
  }

  var initialCallbacks = (0, _dependencies.getCallbacksInLayout)(graphs, paths, layout, {
    outputsOnly: true
  });
  dispatch(startCallbacks(initialCallbacks));
}

var redo = moveHistory('REDO');
exports.redo = redo;
var undo = moveHistory('UNDO');
exports.undo = undo;
var revert = moveHistory('REVERT');
exports.revert = revert;

function moveHistory(changeType) {
  return function (dispatch, getState) {
    var _getState2 = getState(),
        history = _getState2.history,
        paths = _getState2.paths;

    dispatch((0, _reduxActions.createAction)(changeType)());

    var _ref = (changeType === 'REDO' ? history.future[0] : history.past[history.past.length - 1]) || {},
        id = _ref.id,
        props = _ref.props;

    if (id) {
      // Update props
      dispatch((0, _reduxActions.createAction)('UNDO_PROP_CHANGE')({
        itempath: (0, _paths2.getPath)(paths, id),
        props: props
      }));
      dispatch(notifyObservers({
        id: id,
        props: props
      }));
    }
  };
}

function unwrapIfNotMulti(paths, idProps, spec, anyVals, depType) {
  var msg = '';

  if ((0, _dependencies.isMultiValued)(spec)) {
    return [idProps, msg];
  }

  if (idProps.length !== 1) {
    if (!idProps.length) {
      var isStr = typeof spec.id === 'string';
      msg = 'A nonexistent object was used in an `' + depType + '` of a Dash callback. The id of this object is ' + (isStr ? '`' + spec.id + '`' : JSON.stringify(spec.id) + (anyVals ? ' with MATCH values ' + anyVals : '')) + ' and the property is `' + spec.property + (isStr ? '`. The string ids in the current layout are: [' + (0, _ramda.keys)(paths.strs).join(', ') + ']' : '`. The wildcard ids currently available are logged above.');
    } else {
      msg = 'Multiple objects were found for an `' + depType + '` of a callback that only takes one value. The id spec is ' + JSON.stringify(spec.id) + (anyVals ? ' with MATCH values ' + anyVals : '') + ' and the property is `' + spec.property + '`. The objects we found are: ' + JSON.stringify((0, _ramda.map)((0, _ramda.pick)(['id', 'property']), idProps));
    }
  }

  return [idProps[0], msg];
}

function startCallbacks(callbacks) {
  return (/*#__PURE__*/function () {
      var _ref2 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee(dispatch, getState) {
        return regeneratorRuntime.wrap(function _callee$(_context) {
          while (1) {
            switch (_context.prev = _context.next) {
              case 0:
                _context.next = 2;
                return fireReadyCallbacks(dispatch, getState, callbacks);

              case 2:
                return _context.abrupt("return", _context.sent);

              case 3:
              case "end":
                return _context.stop();
            }
          }
        }, _callee);
      }));

      return function (_x, _x2) {
        return _ref2.apply(this, arguments);
      };
    }()
  );
}

function fireReadyCallbacks(_x3, _x4, _x5) {
  return _fireReadyCallbacks.apply(this, arguments);
}

function _fireReadyCallbacks() {
  _fireReadyCallbacks = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee3(dispatch, getState, callbacks) {
    var _findReadyCallbacks, readyCallbacks, blockedCallbacks, _getState6, config, hooks, layout, paths, outputStash, requestedCallbacks, allCallbacks, ids, fireNext, hasClientSide, queue, done;

    return regeneratorRuntime.wrap(function _callee3$(_context3) {
      while (1) {
        switch (_context3.prev = _context3.next) {
          case 0:
            fireNext = function _ref14() {
              return fireReadyCallbacks(dispatch, getState, getState().pendingCallbacks);
            };

            _findReadyCallbacks = (0, _dependencies.findReadyCallbacks)(callbacks), readyCallbacks = _findReadyCallbacks.readyCallbacks, blockedCallbacks = _findReadyCallbacks.blockedCallbacks;
            _getState6 = getState(), config = _getState6.config, hooks = _getState6.hooks, layout = _getState6.layout, paths = _getState6.paths; // We want to calculate all the outputs only once, but we need them
            // for pendingCallbacks which we're going to dispatch prior to
            // initiating the queue. So first loop over readyCallbacks to
            // generate the output lists, then dispatch pendingCallbacks,
            // then loop again to fire off the requests.

            outputStash = {};
            requestedCallbacks = readyCallbacks.map(function (cb) {
              var cbOut = (0, _dependencies.setNewRequestId)(cb);
              var requestId = cbOut.requestId,
                  getOutputs = cbOut.getOutputs;
              var allOutputs = getOutputs(paths);
              var flatOutputs = (0, _ramda.flatten)(allOutputs);
              var allPropIds = [];
              var reqOut = {};
              flatOutputs.forEach(function (_ref11) {
                var id = _ref11.id,
                    property = _ref11.property;
                var idStr = (0, _dependencies.stringifyId)(id);
                var idOut = reqOut[idStr] = reqOut[idStr] || [];
                idOut.push(property);
                allPropIds.push((0, _dependencies.combineIdAndProp)({
                  id: idStr,
                  property: property
                }));
              });
              cbOut.requestedOutputs = reqOut;
              outputStash[requestId] = {
                allOutputs: allOutputs,
                allPropIds: allPropIds
              };
              return cbOut;
            });
            allCallbacks = (0, _ramda.concat)(requestedCallbacks, blockedCallbacks);
            dispatch(setPendingCallbacks(allCallbacks));
            ids = requestedCallbacks.map(function (cb) {
              return [cb.getInputs(paths), cb.getState(paths)];
            });
            _context3.next = 10;
            return (0, _isAppReady["default"])(layout, paths, (0, _ramda.uniq)((0, _ramda.pluck)('id', (0, _ramda.flatten)(ids))));

          case 10:
            hasClientSide = false;
            queue = requestedCallbacks.map(function (cb) {
              var _cb$callback = cb.callback,
                  output = _cb$callback.output,
                  inputs = _cb$callback.inputs,
                  state = _cb$callback.state,
                  clientside_function = _cb$callback.clientside_function;
              var requestId = cb.requestId,
                  resolvedId = cb.resolvedId;
              var _outputStash$requestI = outputStash[requestId],
                  allOutputs = _outputStash$requestI.allOutputs,
                  allPropIds = _outputStash$requestI.allPropIds;
              var payload;

              try {
                var inVals = fillVals(paths, layout, cb, inputs, 'Input', true);

                var preventCallback = function preventCallback() {
                  removeCallbackFromPending(); // no server call here; for performance purposes pretend this is
                  // a clientside callback and defer fireNext for the end
                  // of the currently-ready callbacks.

                  hasClientSide = true;
                  return null;
                };

                if (inVals === null) {
                  return preventCallback();
                }

                var outputs = [];
                var outputErrors = [];
                allOutputs.forEach(function (out, i) {
                  var _unwrapIfNotMulti3 = unwrapIfNotMulti(paths, (0, _ramda.map)((0, _ramda.pick)(['id', 'property']), out), cb.callback.outputs[i], cb.anyVals, 'Output'),
                      _unwrapIfNotMulti4 = _slicedToArray(_unwrapIfNotMulti3, 2),
                      outi = _unwrapIfNotMulti4[0],
                      erri = _unwrapIfNotMulti4[1];

                  outputs.push(outi);

                  if (erri) {
                    outputErrors.push(erri);
                  }
                });

                if (outputErrors.length) {
                  if ((0, _ramda.flatten)(inVals).length) {
                    refErr(outputErrors, paths);
                  } // This case is all-empty multivalued wildcard inputs,
                  // which we would normally fire the callback for, except
                  // some outputs are missing. So instead we treat it like
                  // regular missing inputs and just silently prevent it.


                  return preventCallback();
                }

                payload = {
                  output: output,
                  outputs: (0, _dependencies.isMultiOutputProp)(output) ? outputs : outputs[0],
                  inputs: inVals,
                  changedPropIds: (0, _ramda.keys)(cb.changedPropIds)
                };

                if (cb.callback.state.length) {
                  payload.state = fillVals(paths, layout, cb, state, 'State');
                }
              } catch (e) {
                handleError(e);
                return fireNext();
              }

              function updatePending(pendingCallbacks, skippedProps) {
                var newPending = (0, _dependencies.removePendingCallback)(pendingCallbacks, getState().paths, resolvedId, skippedProps);
                dispatch(setPendingCallbacks(newPending));
              }

              function handleData(data) {
                var _getState7 = getState(),
                    pendingCallbacks = _getState7.pendingCallbacks;

                if (!requestIsActive(pendingCallbacks, resolvedId, requestId)) {
                  return;
                }

                var updated = [];
                Object.entries(data).forEach(function (_ref12) {
                  var _ref13 = _slicedToArray(_ref12, 2),
                      id = _ref13[0],
                      props = _ref13[1];

                  var parsedId = (0, _dependencies.parseIfWildcard)(id);

                  var _getState8 = getState(),
                      oldLayout = _getState8.layout,
                      oldPaths = _getState8.paths;

                  var appliedProps = doUpdateProps(dispatch, getState, parsedId, props);

                  if (appliedProps) {
                    // doUpdateProps can cause new callbacks to be added
                    // via derived props - update pendingCallbacks
                    // But we may also need to merge in other callbacks that
                    // we found in an earlier interation of the data loop.
                    var statePendingCallbacks = getState().pendingCallbacks;

                    if (statePendingCallbacks !== pendingCallbacks) {
                      pendingCallbacks = (0, _dependencies.mergePendingCallbacks)(pendingCallbacks, statePendingCallbacks);
                    }

                    Object.keys(appliedProps).forEach(function (property) {
                      updated.push((0, _dependencies.combineIdAndProp)({
                        id: id,
                        property: property
                      }));
                    });

                    if ((0, _ramda.has)('children', appliedProps)) {
                      var oldChildren = (0, _ramda.path)((0, _ramda.concat)((0, _paths2.getPath)(oldPaths, parsedId), ['props', 'children']), oldLayout); // If components changed, need to update paths,
                      // check if all pending callbacks are still
                      // valid, and add all callbacks associated with
                      // new components, either as inputs or outputs,
                      // or components removed from ALL/ALLSMALLER inputs

                      pendingCallbacks = updateChildPaths(dispatch, getState, pendingCallbacks, parsedId, appliedProps.children, oldChildren);
                    } // persistence edge case: if you explicitly update the
                    // persistence key, other props may change that require us
                    // to fire additional callbacks


                    var addedProps = (0, _ramda.pickBy)(function (v, k) {
                      return !(k in props);
                    }, appliedProps);

                    if (!(0, _ramda.isEmpty)(addedProps)) {
                      var _getState9 = getState(),
                          graphs = _getState9.graphs,
                          _paths = _getState9.paths;

                      pendingCallbacks = includeObservers(id, addedProps, graphs, _paths, pendingCallbacks);
                    }
                  }
                });
                updatePending(pendingCallbacks, (0, _ramda.without)(updated, allPropIds));
              }

              function removeCallbackFromPending() {
                var _getState10 = getState(),
                    pendingCallbacks = _getState10.pendingCallbacks;

                if (requestIsActive(pendingCallbacks, resolvedId, requestId)) {
                  // Skip all prop updates from this callback, and remove
                  // it from the pending list so callbacks it was blocking
                  // that have other changed inputs will still fire.
                  updatePending(pendingCallbacks, allPropIds);
                }
              }

              function handleError(err) {
                removeCallbackFromPending();
                var outputs = payload ? (0, _ramda.map)(_dependencies.combineIdAndProp, (0, _ramda.flatten)([payload.outputs])).join(', ') : output;
                var message = "Callback error updating ".concat(outputs);

                if (clientside_function) {
                  var ns = clientside_function.namespace,
                      fn = clientside_function.function_name;
                  message += " via clientside function ".concat(ns, ".").concat(fn);
                }

                handleAsyncError(err, message, dispatch);
              }

              if (clientside_function) {
                try {
                  handleData(handleClientside(clientside_function, payload));
                } catch (err) {
                  handleError(err);
                }

                hasClientSide = true;
                return null;
              }

              return handleServerside(config, payload, hooks).then(handleData)["catch"](handleError).then(fireNext);
            });
            done = Promise.all(queue);
            return _context3.abrupt("return", hasClientSide ? fireNext().then(done) : done);

          case 14:
          case "end":
            return _context3.stop();
        }
      }
    }, _callee3);
  }));
  return _fireReadyCallbacks.apply(this, arguments);
}

function fillVals(paths, layout, cb, specs, depType, allowAllMissing) {
  var getter = depType === 'Input' ? cb.getInputs : cb.getState;
  var errors = [];
  var emptyMultiValues = 0;
  var inputVals = getter(paths).map(function (inputList, i) {
    var _unwrapIfNotMulti = unwrapIfNotMulti(paths, inputList.map(function (_ref3) {
      var id = _ref3.id,
          property = _ref3.property,
          path_ = _ref3.path;
      return {
        id: id,
        property: property,
        value: (0, _ramda.path)(path_, layout).props[property]
      };
    }), specs[i], cb.anyVals, depType),
        _unwrapIfNotMulti2 = _slicedToArray(_unwrapIfNotMulti, 2),
        inputs = _unwrapIfNotMulti2[0],
        inputError = _unwrapIfNotMulti2[1];

    if ((0, _dependencies.isMultiValued)(specs[i]) && !inputs.length) {
      emptyMultiValues++;
    }

    if (inputError) {
      errors.push(inputError);
    }

    return inputs;
  });

  if (errors.length) {
    if (allowAllMissing && errors.length + emptyMultiValues === inputVals.length) {
      // We have at least one non-multivalued input, but all simple and
      // multi-valued inputs are missing.
      // (if all inputs are multivalued and all missing we still return
      // them as normal, and fire the callback.)
      return null;
    } // If we get here we have some missing and some present inputs.
    // Or all missing in a context that doesn't allow this.
    // That's a real problem, so throw the first message as an error.


    refErr(errors, paths);
  }

  return inputVals;
}

function refErr(errors, paths) {
  var err = errors[0];

  if (err.indexOf('logged above') !== -1) {
    // Wildcard reference errors mention a list of wildcard specs logged
    // TODO: unwrapped list of wildcard ids?
    // eslint-disable-next-line no-console
    console.error(paths.objs);
  }

  throw new ReferenceError(err);
}

function handleServerside(config, payload, hooks) {
  if (hooks.request_pre !== null) {
    hooks.request_pre(payload);
  }

  return fetch("".concat((0, _utils.urlBase)(config), "_dash-update-component"), (0, _ramda.mergeDeepRight)(config.fetch, {
    method: 'POST',
    headers: getCSRFHeader(),
    body: JSON.stringify(payload)
  })).then(function (res) {
    var status = res.status;

    if (status === _constants3.STATUS.OK) {
      return res.json().then(function (data) {
        var multi = data.multi,
            response = data.response;

        if (hooks.request_post !== null) {
          hooks.request_post(payload, response);
        }

        if (multi) {
          return response;
        }

        var output = payload.output;
        var id = output.substr(0, output.lastIndexOf('.'));
        return _defineProperty({}, id, response.props);
      });
    }

    if (status === _constants3.STATUS.PREVENT_UPDATE) {
      return {};
    }

    throw res;
  });
}

var getVals = function getVals(input) {
  return Array.isArray(input) ? (0, _ramda.pluck)('value', input) : input.value;
};

var zipIfArray = function zipIfArray(a, b) {
  return Array.isArray(a) ? (0, _ramda.zip)(a, b) : [[a, b]];
};

function handleClientside(clientside_function, payload) {
  var dc = window.dash_clientside = window.dash_clientside || {};

  if (!dc.no_update) {
    Object.defineProperty(dc, 'no_update', {
      value: {
        description: 'Return to prevent updating an Output.'
      },
      writable: false
    });
    Object.defineProperty(dc, 'PreventUpdate', {
      value: {
        description: 'Throw to prevent updating all Outputs.'
      },
      writable: false
    });
  }

  var inputs = payload.inputs,
      outputs = payload.outputs,
      state = payload.state;
  var returnValue;

  try {
    var _dc$namespace;

    var namespace = clientside_function.namespace,
        function_name = clientside_function.function_name;
    var args = inputs.map(getVals);

    if (state) {
      args = (0, _ramda.concat)(args, state.map(getVals));
    }

    returnValue = (_dc$namespace = dc[namespace])[function_name].apply(_dc$namespace, _toConsumableArray(args));
  } catch (e) {
    if (e === dc.PreventUpdate) {
      return {};
    }

    throw e;
  }

  if ((0, _ramda.type)(returnValue) === 'Promise') {
    throw new Error('The clientside function returned a Promise. ' + 'Promises are not supported in Dash clientside ' + 'right now, but may be in the future.');
  }

  var data = {};
  zipIfArray(outputs, returnValue).forEach(function (_ref5) {
    var _ref6 = _slicedToArray(_ref5, 2),
        outi = _ref6[0],
        reti = _ref6[1];

    zipIfArray(outi, reti).forEach(function (_ref7) {
      var _ref8 = _slicedToArray(_ref7, 2),
          outij = _ref8[0],
          retij = _ref8[1];

      var id = outij.id,
          property = outij.property;
      var idStr = (0, _dependencies.stringifyId)(id);
      var dataForId = data[idStr] = data[idStr] || {};

      if (retij !== dc.no_update) {
        dataForId[property] = retij;
      }
    });
  });
  return data;
}

function requestIsActive(pendingCallbacks, resolvedId, requestId) {
  var thisCallback = pendingCallbacks.find((0, _ramda.propEq)('resolvedId', resolvedId)); // could be inactivated if it was requested again, in which case it could
  // potentially even have finished and been removed from the list

  return thisCallback && thisCallback.requestId === requestId;
}

function doUpdateProps(dispatch, getState, id, updatedProps) {
  var _getState3 = getState(),
      layout = _getState3.layout,
      paths = _getState3.paths;

  var itempath = (0, _paths2.getPath)(paths, id);

  if (!itempath) {
    return false;
  } // This is a callback-generated update.
  // Check if this invalidates existing persisted prop values,
  // or if persistence changed, whether this updates other props.


  var updatedProps2 = (0, _persistence.prunePersistence)((0, _ramda.path)(itempath, layout), updatedProps, dispatch); // In case the update contains whole components, see if any of
  // those components have props to update to persist user edits.

  var _applyPersistence = (0, _persistence.applyPersistence)({
    props: updatedProps2
  }, dispatch),
      props = _applyPersistence.props;

  dispatch(updateProps({
    itempath: itempath,
    props: props,
    source: 'response'
  }));
  return props;
}

function updateChildPaths(dispatch, getState, pendingCallbacks, id, children, oldChildren) {
  var _getState4 = getState(),
      oldPaths = _getState4.paths,
      graphs = _getState4.graphs;

  var childrenPath = (0, _ramda.concat)((0, _paths2.getPath)(oldPaths, id), ['props', 'children']);
  var paths = (0, _paths2.computePaths)(children, childrenPath, oldPaths);
  dispatch(setPaths(paths));
  var cleanedCallbacks = (0, _dependencies.pruneRemovedCallbacks)(pendingCallbacks, paths);
  var newCallbacks = (0, _dependencies.getCallbacksInLayout)(graphs, paths, children, {
    chunkPath: childrenPath
  }); // Wildcard callbacks with array inputs (ALL / ALLSMALLER) need to trigger
  // even due to the deletion of components

  var deletedComponentCallbacks = (0, _dependencies.getCallbacksInLayout)(graphs, oldPaths, oldChildren, {
    removedArrayInputsOnly: true,
    newPaths: paths,
    chunkPath: childrenPath
  });
  var allNewCallbacks = (0, _dependencies.mergePendingCallbacks)(newCallbacks, deletedComponentCallbacks);
  return (0, _dependencies.mergePendingCallbacks)(cleanedCallbacks, allNewCallbacks);
}

function notifyObservers(_ref9) {
  var id = _ref9.id,
      props = _ref9.props;
  return (/*#__PURE__*/function () {
      var _ref10 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2(dispatch, getState) {
        var _getState5, graphs, paths, pendingCallbacks, finalCallbacks;

        return regeneratorRuntime.wrap(function _callee2$(_context2) {
          while (1) {
            switch (_context2.prev = _context2.next) {
              case 0:
                _getState5 = getState(), graphs = _getState5.graphs, paths = _getState5.paths, pendingCallbacks = _getState5.pendingCallbacks;
                finalCallbacks = includeObservers(id, props, graphs, paths, pendingCallbacks);
                dispatch(startCallbacks(finalCallbacks));

              case 3:
              case "end":
                return _context2.stop();
            }
          }
        }, _callee2);
      }));

      return function (_x6, _x7) {
        return _ref10.apply(this, arguments);
      };
    }()
  );
}

function includeObservers(id, props, graphs, paths, pendingCallbacks) {
  var changedProps = (0, _ramda.keys)(props);
  var finalCallbacks = pendingCallbacks;
  changedProps.forEach(function (propName) {
    var newCBs = (0, _dependencies.getCallbacksByInput)(graphs, paths, id, propName);

    if (newCBs.length) {
      finalCallbacks = (0, _dependencies.mergePendingCallbacks)(finalCallbacks, (0, _dependencies.followForward)(graphs, paths, newCBs));
    }
  });
  return finalCallbacks;
}

function handleAsyncError(err, message, dispatch) {
  // Handle html error responses
  if (err && typeof err.text === 'function') {
    err.text().then(function (text) {
      var error = {
        message: message,
        html: text
      };
      dispatch(onError({
        type: 'backEnd',
        error: error
      }));
    });
  } else {
    var error = err instanceof Error ? err : {
      message: message,
      html: err
    };
    dispatch(onError({
      type: 'backEnd',
      error: error
    }));
  }
}