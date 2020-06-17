"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.getCallbacksByInput = getCallbacksByInput;
exports.getPriority = getPriority;
exports.includeObservers = includeObservers;
exports.pruneCallbacks = pruneCallbacks;
exports.resolveDeps = resolveDeps;
exports.makeResolvedCallback = exports.getUniqueIdentifier = exports.getLayoutCallbacks = exports.getReadyCallbacks = exports.combineIdAndProp = exports.mergeMax = exports.INDIRECT = exports.DIRECT = void 0;

var _ramda = require("ramda");

var _dependencies = require("./dependencies");

var _paths = require("./paths");

function _toConsumableArray(arr) { return _arrayWithoutHoles(arr) || _iterableToArray(arr) || _nonIterableSpread(); }

function _nonIterableSpread() { throw new TypeError("Invalid attempt to spread non-iterable instance"); }

function _iterableToArray(iter) { if (Symbol.iterator in Object(iter) || Object.prototype.toString.call(iter) === "[object Arguments]") return Array.from(iter); }

function _arrayWithoutHoles(arr) { if (Array.isArray(arr)) { for (var i = 0, arr2 = new Array(arr.length); i < arr.length; i++) { arr2[i] = arr[i]; } return arr2; } }

function ownKeys(object, enumerableOnly) { var keys = Object.keys(object); if (Object.getOwnPropertySymbols) { var symbols = Object.getOwnPropertySymbols(object); if (enumerableOnly) symbols = symbols.filter(function (sym) { return Object.getOwnPropertyDescriptor(object, sym).enumerable; }); keys.push.apply(keys, symbols); } return keys; }

function _objectSpread(target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i] != null ? arguments[i] : {}; if (i % 2) { ownKeys(Object(source), true).forEach(function (key) { _defineProperty(target, key, source[key]); }); } else if (Object.getOwnPropertyDescriptors) { Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)); } else { ownKeys(Object(source)).forEach(function (key) { Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key)); }); } } return target; }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

function _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance"); }

function _iterableToArrayLimit(arr, i) { if (!(Symbol.iterator in Object(arr) || Object.prototype.toString.call(arr) === "[object Arguments]")) { return; } var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

var DIRECT = 2;
exports.DIRECT = DIRECT;
var INDIRECT = 1;
exports.INDIRECT = INDIRECT;
var mergeMax = (0, _ramda.mergeWith)(Math.max);
exports.mergeMax = mergeMax;

var combineIdAndProp = function combineIdAndProp(_ref) {
  var id = _ref.id,
      property = _ref.property;
  return "".concat((0, _dependencies.stringifyId)(id), ".").concat(property);
};

exports.combineIdAndProp = combineIdAndProp;

function getCallbacksByInput(graphs, paths, id, prop, changeType) {
  var withPriority = arguments.length > 5 && arguments[5] !== undefined ? arguments[5] : true;
  var matches = [];
  var idAndProp = combineIdAndProp({
    id: id,
    property: prop
  });

  if (typeof id === 'string') {
    // standard id version
    var callbacks = (graphs.inputMap[id] || {})[prop];

    if (!callbacks) {
      return [];
    }

    callbacks.forEach((0, _dependencies.addAllResolvedFromOutputs)(resolveDeps(), paths, matches));
  } else {
    // wildcard version
    var _keys = Object.keys(id).sort();

    var vals = (0, _ramda.props)(_keys, id);

    var keyStr = _keys.join(',');

    var patterns = (graphs.inputPatterns[keyStr] || {})[prop];

    if (!patterns) {
      return [];
    }

    patterns.forEach(function (pattern) {
      if ((0, _dependencies.idMatch)(_keys, vals, pattern.values)) {
        pattern.callbacks.forEach((0, _dependencies.addAllResolvedFromOutputs)(resolveDeps(_keys, vals, pattern.values), paths, matches));
      }
    });
  }

  matches.forEach(function (match) {
    match.changedPropIds[idAndProp] = changeType || DIRECT;

    if (withPriority) {
      match.priority = getPriority(graphs, paths, match);
    }
  });
  return matches;
}
/*
 * Builds a tree of all callbacks that can be triggered by the provided callback.
 * Uses the number of callbacks at each tree depth and the total depth of the tree
 * to create a sortable priority hash.
 */


function getPriority(graphs, paths, callback) {
  var callbacks = [callback];
  var touchedOutputs = {};
  var priority = [];

  while (callbacks.length) {
    var outputs = (0, _ramda.filter)(function (o) {
      return !touchedOutputs[combineIdAndProp(o)];
    }, (0, _ramda.flatten)((0, _ramda.map)(function (cb) {
      return (0, _ramda.flatten)(cb.getOutputs(paths));
    }, callbacks)));
    touchedOutputs = (0, _ramda.reduce)(function (touched, o) {
      return (0, _ramda.assoc)(combineIdAndProp(o), true, touched);
    }, touchedOutputs, outputs);
    callbacks = (0, _ramda.flatten)((0, _ramda.map)(function (_ref2) {
      var id = _ref2.id,
          property = _ref2.property;
      return getCallbacksByInput(graphs, paths, id, property, INDIRECT, false);
    }, outputs));

    if (callbacks.length) {
      priority.push(callbacks.length);
    }
  }

  priority.unshift(priority.length);
  return (0, _ramda.map)(function (i) {
    return Math.min(i, 35).toString(36);
  }, priority).join('');
}

var getReadyCallbacks = function getReadyCallbacks(paths, candidates) {
  var callbacks = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : candidates;

  // Skip if there's no candidates
  if (!candidates.length) {
    return [];
  } // Find all outputs of all active callbacks


  var outputs = (0, _ramda.map)(combineIdAndProp, (0, _ramda.reduce)(function (o, cb) {
    return (0, _ramda.concat)(o, (0, _ramda.flatten)(cb.getOutputs(paths)));
  }, [], callbacks)); // Make `outputs` hash table for faster access

  var outputsMap = {};
  (0, _ramda.forEach)(function (output) {
    return outputsMap[output] = true;
  }, outputs); // Find `requested` callbacks that do not depend on a outstanding output (as either input or state)

  return (0, _ramda.filter)(function (cb) {
    return (0, _ramda.all)(function (cbp) {
      return !outputsMap[combineIdAndProp(cbp)];
    }, (0, _ramda.flatten)(cb.getInputs(paths)));
  }, candidates);
};

exports.getReadyCallbacks = getReadyCallbacks;

var getLayoutCallbacks = function getLayoutCallbacks(graphs, paths, layout, options) {
  var exclusions = [];
  var callbacks = (0, _dependencies.getUnfilteredLayoutCallbacks)(graphs, paths, layout, options);
  /*
      Remove from the initial callbacks those that are left with only excluded inputs.
       Exclusion of inputs happens when:
      - an input is missing
      - an input in the initial callback chain depends only on excluded inputs
       Further execlusion might happen after callbacks return with:
      - PreventUpdate
      - no_update
  */

  while (true) {
    // Find callbacks for which all inputs are missing or in the exclusions
    var _partition = (0, _ramda.partition)(function (_ref3) {
      var inputs = _ref3.callback.inputs,
          getInputs = _ref3.getInputs;
      return (0, _ramda.all)(_dependencies.isMultiValued, inputs) || !(0, _ramda.isEmpty)((0, _ramda.difference)((0, _ramda.map)(combineIdAndProp, (0, _ramda.flatten)(getInputs(paths))), exclusions));
    }, callbacks),
        _partition2 = _slicedToArray(_partition, 2),
        included = _partition2[0],
        excluded = _partition2[1]; // If there's no additional exclusions, break loop - callbacks have been cleaned


    if (!excluded.length) {
      break;
    }

    callbacks = included; // update exclusions with all additional excluded outputs

    exclusions = (0, _ramda.concat)(exclusions, (0, _ramda.map)(combineIdAndProp, (0, _ramda.flatten)((0, _ramda.map)(function (_ref4) {
      var getOutputs = _ref4.getOutputs;
      return getOutputs(paths);
    }, excluded))));
  }
  /*
      Return all callbacks with an `executionGroup` to allow group-processing
  */


  var executionGroup = Math.random().toString(16);
  return (0, _ramda.map)(function (cb) {
    return _objectSpread({}, cb, {
      executionGroup: executionGroup
    });
  }, callbacks);
};

exports.getLayoutCallbacks = getLayoutCallbacks;

var getUniqueIdentifier = function getUniqueIdentifier(_ref5) {
  var anyVals = _ref5.anyVals,
      _ref5$callback = _ref5.callback,
      inputs = _ref5$callback.inputs,
      outputs = _ref5$callback.outputs,
      state = _ref5$callback.state;
  return (0, _ramda.concat)((0, _ramda.map)(combineIdAndProp, [].concat(_toConsumableArray(inputs), _toConsumableArray(outputs), _toConsumableArray(state))), Array.isArray(anyVals) ? anyVals : anyVals === '' ? [] : [anyVals]).join(',');
};

exports.getUniqueIdentifier = getUniqueIdentifier;

function includeObservers(id, properties, graphs, paths) {
  return (0, _ramda.flatten)((0, _ramda.map)(function (propName) {
    return getCallbacksByInput(graphs, paths, id, propName);
  }, (0, _ramda.keys)(properties)));
}
/*
 * Create a pending callback object. Includes the original callback definition,
 * its resolved ID (including the value of all MATCH wildcards),
 * accessors to find all inputs, outputs, and state involved in this
 * callback (lazy as not all users will want all of these).
 */


var makeResolvedCallback = function makeResolvedCallback(callback, resolve, anyVals) {
  return {
    callback: callback,
    anyVals: anyVals,
    resolvedId: callback.output + anyVals,
    getOutputs: function getOutputs(paths) {
      return callback.outputs.map(resolve(paths));
    },
    getInputs: function getInputs(paths) {
      return callback.inputs.map(resolve(paths));
    },
    getState: function getState(paths) {
      return callback.state.map(resolve(paths));
    },
    changedPropIds: {},
    initialCall: false
  };
};

exports.makeResolvedCallback = makeResolvedCallback;

function pruneCallbacks(callbacks, paths) {
  var _partition3 = (0, _ramda.partition)(function (_ref6) {
    var getOutputs = _ref6.getOutputs,
        outputs = _ref6.callback.outputs;
    return (0, _ramda.flatten)(getOutputs(paths)).length === outputs.length;
  }, callbacks),
      _partition4 = _slicedToArray(_partition3, 2),
      removed = _partition4[1];

  var _partition5 = (0, _ramda.partition)(function (_ref7) {
    var getOutputs = _ref7.getOutputs;
    return !(0, _ramda.flatten)(getOutputs(paths)).length;
  }, removed),
      _partition6 = _slicedToArray(_partition5, 2),
      modified = _partition6[1];

  var added = (0, _ramda.map)(function (cb) {
    return (0, _ramda.assoc)('changedPropIds', (0, _ramda.pickBy)(function (_, propId) {
      return (0, _paths.getPath)(paths, (0, _dependencies.splitIdAndProp)(propId).id);
    }, cb.changedPropIds), cb);
  }, modified);
  return {
    added: added,
    removed: removed
  };
}

function resolveDeps(refKeys, refVals, refPatternVals) {
  return function (paths) {
    return function (_ref8) {
      var idPattern = _ref8.id,
          property = _ref8.property;

      if (typeof idPattern === 'string') {
        var path = (0, _paths.getPath)(paths, idPattern);
        return path ? [{
          id: idPattern,
          property: property,
          path: path
        }] : [];
      }

      var _keys = Object.keys(idPattern).sort();

      var patternVals = (0, _ramda.props)(_keys, idPattern);

      var keyStr = _keys.join(',');

      var keyPaths = paths.objs[keyStr];

      if (!keyPaths) {
        return [];
      }

      var result = [];
      keyPaths.forEach(function (_ref9) {
        var vals = _ref9.values,
            path = _ref9.path;

        if ((0, _dependencies.idMatch)(_keys, vals, patternVals, refKeys, refVals, refPatternVals)) {
          result.push({
            id: (0, _ramda.zipObj)(_keys, vals),
            property: property,
            path: path
          });
        }
      });
      return result;
    };
  };
}