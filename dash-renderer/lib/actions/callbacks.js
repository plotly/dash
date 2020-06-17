"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.executeCallback = executeCallback;
exports.aggregateCallbacks = exports.removeWatchedCallbacks = exports.removeStoredCallbacks = exports.removeRequestedCallbacks = exports.removePrioritizedCallbacks = exports.removeExecutingCallbacks = exports.removeBlockedCallbacks = exports.removeExecutedCallbacks = exports.addWatchedCallbacks = exports.addStoredCallbacks = exports.addRequestedCallbacks = exports.addPrioritizedCallbacks = exports.addExecutingCallbacks = exports.addExecutedCallbacks = exports.addCompletedCallbacks = exports.addBlockedCallbacks = void 0;

var _ramda = require("ramda");

var _constants = require("../constants/constants");

var _callbacks = require("../reducers/callbacks");

var _dependencies = require("./dependencies");

var _utils = require("./utils");

var _ = require(".");

var _reduxActions = require("redux-actions");

function ownKeys(object, enumerableOnly) { var keys = Object.keys(object); if (Object.getOwnPropertySymbols) { var symbols = Object.getOwnPropertySymbols(object); if (enumerableOnly) symbols = symbols.filter(function (sym) { return Object.getOwnPropertyDescriptor(object, sym).enumerable; }); keys.push.apply(keys, symbols); } return keys; }

function _objectSpread(target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i] != null ? arguments[i] : {}; if (i % 2) { ownKeys(Object(source), true).forEach(function (key) { _defineProperty(target, key, source[key]); }); } else if (Object.getOwnPropertyDescriptors) { Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)); } else { ownKeys(Object(source)).forEach(function (key) { Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key)); }); } } return target; }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

function _toConsumableArray(arr) { return _arrayWithoutHoles(arr) || _iterableToArray(arr) || _nonIterableSpread(); }

function _nonIterableSpread() { throw new TypeError("Invalid attempt to spread non-iterable instance"); }

function _iterableToArray(iter) { if (Symbol.iterator in Object(iter) || Object.prototype.toString.call(iter) === "[object Arguments]") return Array.from(iter); }

function _arrayWithoutHoles(arr) { if (Array.isArray(arr)) { for (var i = 0, arr2 = new Array(arr.length); i < arr.length; i++) { arr2[i] = arr[i]; } return arr2; } }

function _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance"); }

function _iterableToArrayLimit(arr, i) { if (!(Symbol.iterator in Object(arr) || Object.prototype.toString.call(arr) === "[object Arguments]")) { return; } var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

var addBlockedCallbacks = (0, _reduxActions.createAction)(_callbacks.CallbackActionType.AddBlocked);
exports.addBlockedCallbacks = addBlockedCallbacks;
var addCompletedCallbacks = (0, _reduxActions.createAction)(_callbacks.CallbackAggregateActionType.AddCompleted);
exports.addCompletedCallbacks = addCompletedCallbacks;
var addExecutedCallbacks = (0, _reduxActions.createAction)(_callbacks.CallbackActionType.AddExecuted);
exports.addExecutedCallbacks = addExecutedCallbacks;
var addExecutingCallbacks = (0, _reduxActions.createAction)(_callbacks.CallbackActionType.AddExecuting);
exports.addExecutingCallbacks = addExecutingCallbacks;
var addPrioritizedCallbacks = (0, _reduxActions.createAction)(_callbacks.CallbackActionType.AddPrioritized);
exports.addPrioritizedCallbacks = addPrioritizedCallbacks;
var addRequestedCallbacks = (0, _reduxActions.createAction)(_callbacks.CallbackActionType.AddRequested);
exports.addRequestedCallbacks = addRequestedCallbacks;
var addStoredCallbacks = (0, _reduxActions.createAction)(_callbacks.CallbackActionType.AddStored);
exports.addStoredCallbacks = addStoredCallbacks;
var addWatchedCallbacks = (0, _reduxActions.createAction)(_callbacks.CallbackActionType.AddWatched);
exports.addWatchedCallbacks = addWatchedCallbacks;
var removeExecutedCallbacks = (0, _reduxActions.createAction)(_callbacks.CallbackActionType.RemoveExecuted);
exports.removeExecutedCallbacks = removeExecutedCallbacks;
var removeBlockedCallbacks = (0, _reduxActions.createAction)(_callbacks.CallbackActionType.RemoveBlocked);
exports.removeBlockedCallbacks = removeBlockedCallbacks;
var removeExecutingCallbacks = (0, _reduxActions.createAction)(_callbacks.CallbackActionType.RemoveExecuting);
exports.removeExecutingCallbacks = removeExecutingCallbacks;
var removePrioritizedCallbacks = (0, _reduxActions.createAction)(_callbacks.CallbackActionType.RemovePrioritized);
exports.removePrioritizedCallbacks = removePrioritizedCallbacks;
var removeRequestedCallbacks = (0, _reduxActions.createAction)(_callbacks.CallbackActionType.RemoveRequested);
exports.removeRequestedCallbacks = removeRequestedCallbacks;
var removeStoredCallbacks = (0, _reduxActions.createAction)(_callbacks.CallbackActionType.RemoveStored);
exports.removeStoredCallbacks = removeStoredCallbacks;
var removeWatchedCallbacks = (0, _reduxActions.createAction)(_callbacks.CallbackActionType.RemoveWatched);
exports.removeWatchedCallbacks = removeWatchedCallbacks;
var aggregateCallbacks = (0, _reduxActions.createAction)(_callbacks.CallbackAggregateActionType.Aggregate);
exports.aggregateCallbacks = aggregateCallbacks;

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

function fillVals(paths, layout, cb, specs, depType) {
  var allowAllMissing = arguments.length > 5 && arguments[5] !== undefined ? arguments[5] : false;
  var getter = depType === 'Input' ? cb.getInputs : cb.getState;
  var errors = [];
  var emptyMultiValues = 0;
  var inputVals = getter(paths).map(function (inputList, i) {
    var _unwrapIfNotMulti = unwrapIfNotMulti(paths, inputList.map(function (_ref) {
      var id = _ref.id,
          property = _ref.property,
          path_ = _ref.path;
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

var getVals = function getVals(input) {
  return Array.isArray(input) ? (0, _ramda.pluck)('value', input) : input.value;
};

var zipIfArray = function zipIfArray(a, b) {
  return Array.isArray(a) ? (0, _ramda.zip)(a, b) : [[a, b]];
};

function handleClientside(clientside_function, payload) {
  var _returnValue;

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
    } // setup callback context


    var input_dict = inputsToDict(inputs);
    dc.callback_context = {};
    dc.callback_context.triggered = payload.changedPropIds.map(function (prop_id) {
      return {
        prop_id: prop_id,
        value: input_dict[prop_id]
      };
    });
    dc.callback_context.inputs_list = inputs;
    dc.callback_context.inputs = input_dict;
    dc.callback_context.states_list = state;
    dc.callback_context.states = inputsToDict(state);
    returnValue = (_dc$namespace = dc[namespace])[function_name].apply(_dc$namespace, _toConsumableArray(args));
  } catch (e) {
    if (e === dc.PreventUpdate) {
      return {};
    }

    throw e;
  } finally {
    delete dc.callback_context;
  }

  if (typeof ((_returnValue = returnValue) === null || _returnValue === void 0 ? void 0 : _returnValue.then) === 'function') {
    throw new Error('The clientside function returned a Promise. ' + 'Promises are not supported in Dash clientside ' + 'right now, but may be in the future.');
  }

  var data = {};
  zipIfArray(outputs, returnValue).forEach(function (_ref2) {
    var _ref3 = _slicedToArray(_ref2, 2),
        outi = _ref3[0],
        reti = _ref3[1];

    zipIfArray(outi, reti).forEach(function (_ref4) {
      var _ref5 = _slicedToArray(_ref4, 2),
          outij = _ref5[0],
          retij = _ref5[1];

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

function handleServerside(hooks, config, payload) {
  if (hooks.request_pre !== null) {
    hooks.request_pre(payload);
  }

  return fetch("".concat((0, _utils.urlBase)(config), "_dash-update-component"), (0, _ramda.mergeDeepRight)(config.fetch, {
    method: 'POST',
    headers: (0, _.getCSRFHeader)(),
    body: JSON.stringify(payload)
  })).then(function (res) {
    var status = res.status;

    if (status === _constants.STATUS.OK) {
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

    if (status === _constants.STATUS.PREVENT_UPDATE) {
      return {};
    }

    throw res;
  }, function () {
    // fetch rejection - this means the request didn't return,
    // we don't get here from 400/500 errors, only network
    // errors or unresponsive servers.
    throw new Error('Callback failed: the server did not respond.');
  });
}

function inputsToDict(inputs_list) {
  // Ported directly from _utils.py, inputs_to_dict
  // takes an array of inputs (some inputs may be an array)
  // returns an Object (map):
  //  keys of the form `id.property` or `{"id": 0}.property`
  //  values contain the property value
  if (!inputs_list) {
    return {};
  }

  var inputs = {};

  for (var i = 0; i < inputs_list.length; i++) {
    if (Array.isArray(inputs_list[i])) {
      var inputsi = inputs_list[i];

      for (var ii = 0; ii < inputsi.length; ii++) {
        var _inputsi$ii$value;

        var id_str = "".concat((0, _dependencies.stringifyId)(inputsi[ii].id), ".").concat(inputsi[ii].property);
        inputs[id_str] = (_inputsi$ii$value = inputsi[ii].value) !== null && _inputsi$ii$value !== void 0 ? _inputsi$ii$value : null;
      }
    } else {
      var _inputs_list$i$value;

      var _id_str = "".concat((0, _dependencies.stringifyId)(inputs_list[i].id), ".").concat(inputs_list[i].property);

      inputs[_id_str] = (_inputs_list$i$value = inputs_list[i].value) !== null && _inputs_list$i$value !== void 0 ? _inputs_list$i$value : null;
    }
  }

  return inputs;
}

function executeCallback(cb, config, hooks, paths, layout, _ref7) {
  var allOutputs = _ref7.allOutputs;
  var _cb$callback = cb.callback,
      output = _cb$callback.output,
      inputs = _cb$callback.inputs,
      state = _cb$callback.state,
      clientside_function = _cb$callback.clientside_function;

  try {
    var inVals = fillVals(paths, layout, cb, inputs, 'Input', true);
    /* Prevent callback if there's no inputs */

    if (inVals === null) {
      return _objectSpread({}, cb, {
        executionPromise: null
      });
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


      return _objectSpread({}, cb, {
        executionPromise: null
      });
    }

    var __promise = new Promise(function (resolve) {
      try {
        var payload = {
          output: output,
          outputs: (0, _dependencies.isMultiOutputProp)(output) ? outputs : outputs[0],
          inputs: inVals,
          changedPropIds: (0, _ramda.keys)(cb.changedPropIds),
          state: cb.callback.state.length ? fillVals(paths, layout, cb, state, 'State') : undefined
        };

        if (clientside_function) {
          try {
            resolve({
              data: handleClientside(clientside_function, payload),
              payload: payload
            });
          } catch (error) {
            resolve({
              error: error,
              payload: payload
            });
          }

          return null;
        } else {
          handleServerside(hooks, config, payload).then(function (data) {
            return resolve({
              data: data,
              payload: payload
            });
          })["catch"](function (error) {
            return resolve({
              error: error,
              payload: payload
            });
          });
        }
      } catch (error) {
        resolve({
          error: error,
          payload: null
        });
      }
    });

    var newCb = _objectSpread({}, cb, {
      executionPromise: __promise
    });

    return newCb;
  } catch (error) {
    return _objectSpread({}, cb, {
      executionPromise: {
        error: error,
        payload: null
      }
    });
  }
}