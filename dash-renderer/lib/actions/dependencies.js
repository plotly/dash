"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.splitIdAndProp = splitIdAndProp;
exports.parseIfWildcard = parseIfWildcard;
exports.stringifyId = stringifyId;
exports.validateCallbacksToLayout = validateCallbacksToLayout;
exports.computeGraphs = computeGraphs;
exports.idMatch = idMatch;
exports.isMultiValued = isMultiValued;
exports.addAllResolvedFromOutputs = addAllResolvedFromOutputs;
exports.getWatchedKeys = getWatchedKeys;
exports.getUnfilteredLayoutCallbacks = getUnfilteredLayoutCallbacks;
exports.isMultiOutputProp = void 0;

var _dependencyGraph = require("dependency-graph");

var _fastIsnumeric = _interopRequireDefault(require("fast-isnumeric"));

var _ramda = require("ramda");

var _dependencies_ts = require("./dependencies_ts");

var _paths = require("./paths");

var _utils = require("./utils");

var _registry = _interopRequireDefault(require("../registry"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

function ownKeys(object, enumerableOnly) { var keys = Object.keys(object); if (Object.getOwnPropertySymbols) { var symbols = Object.getOwnPropertySymbols(object); if (enumerableOnly) symbols = symbols.filter(function (sym) { return Object.getOwnPropertyDescriptor(object, sym).enumerable; }); keys.push.apply(keys, symbols); } return keys; }

function _objectSpread(target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i] != null ? arguments[i] : {}; if (i % 2) { ownKeys(Object(source), true).forEach(function (key) { _defineProperty(target, key, source[key]); }); } else if (Object.getOwnPropertyDescriptors) { Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)); } else { ownKeys(Object(source)).forEach(function (key) { Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key)); }); } } return target; }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

function _createForOfIteratorHelper(o, allowArrayLike) { var it; if (typeof Symbol === "undefined" || o[Symbol.iterator] == null) { if (Array.isArray(o) || (it = _unsupportedIterableToArray(o)) || allowArrayLike && o && typeof o.length === "number") { if (it) o = it; var i = 0; var F = function F() {}; return { s: F, n: function n() { if (i >= o.length) return { done: true }; return { done: false, value: o[i++] }; }, e: function e(_e2) { throw _e2; }, f: F }; } throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); } var normalCompletion = true, didErr = false, err; return { s: function s() { it = o[Symbol.iterator](); }, n: function n() { var step = it.next(); normalCompletion = step.done; return step; }, e: function e(_e3) { didErr = true; err = _e3; }, f: function f() { try { if (!normalCompletion && it["return"] != null) it["return"](); } finally { if (didErr) throw err; } } }; }

function _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _unsupportedIterableToArray(arr, i) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function _iterableToArrayLimit(arr, i) { if (typeof Symbol === "undefined" || !(Symbol.iterator in Object(arr))) return; var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

/*
 * If this update is for multiple outputs, then it has
 * starting & trailing `..` and each propId pair is separated
 * by `...`, e.g.
 * "..output-1.value...output-2.value...output-3.value...output-4.value.."
 */
var isMultiOutputProp = function isMultiOutputProp(idAndProp) {
  return idAndProp.startsWith('..');
};

exports.isMultiOutputProp = isMultiOutputProp;
var ALL = {
  wild: 'ALL',
  multi: 1
};
var MATCH = {
  wild: 'MATCH'
};
var ALLSMALLER = {
  wild: 'ALLSMALLER',
  multi: 1,
  expand: 1
};
var wildcards = {
  ALL: ALL,
  MATCH: MATCH,
  ALLSMALLER: ALLSMALLER
};
var allowedWildcards = {
  Output: {
    ALL: ALL,
    MATCH: MATCH
  },
  Input: wildcards,
  State: wildcards
};
var wildcardValTypes = ['string', 'number', 'boolean'];
var idInvalidChars = ['.', '{'];
/*
 * If this ID is a wildcard, it is a stringified JSON object
 * the "{" character is disallowed from regular string IDs
 */

var isWildcardId = function isWildcardId(idStr) {
  return idStr.startsWith('{');
};
/*
 * Turn stringified wildcard IDs into objects.
 * Wildcards are encoded as single-item arrays containing the wildcard name
 * as a string.
 */


function parseWildcardId(idStr) {
  return (0, _ramda.map)(function (val) {
    return Array.isArray(val) && wildcards[val[0]] || val;
  }, JSON.parse(idStr));
}
/*
 * If this update is for multiple outputs, then it has
 * starting & trailing `..` and each propId pair is separated
 * by `...`, e.g.
 * "..output-1.value...output-2.value...output-3.value...output-4.value.."
 */


function parseMultipleOutputs(outputIdAndProp) {
  return outputIdAndProp.substr(2, outputIdAndProp.length - 4).split('...');
}

function splitIdAndProp(idAndProp) {
  // since wildcard ids can have . in them but props can't,
  // look for the last . in the string and split there
  var dotPos = idAndProp.lastIndexOf('.');
  var idStr = idAndProp.substr(0, dotPos);
  return {
    id: parseIfWildcard(idStr),
    property: idAndProp.substr(dotPos + 1)
  };
}
/*
 * Check if this ID is a stringified object, and if so parse it to that object
 */


function parseIfWildcard(idStr) {
  return isWildcardId(idStr) ? parseWildcardId(idStr) : idStr;
}
/*
 * JSON.stringify - for the object form - but ensuring keys are sorted
 */


function stringifyId(id) {
  if (_typeof(id) !== 'object') {
    return id;
  }

  var stringifyVal = function stringifyVal(v) {
    return v && v.wild || JSON.stringify(v);
  };

  var parts = Object.keys(id).sort().map(function (k) {
    return JSON.stringify(k) + ':' + stringifyVal(id[k]);
  });
  return '{' + parts.join(',') + '}';
}
/*
 * id dict values can be numbers, strings, and booleans.
 * We need a definite ordering that will work across types,
 * even if sane users would not mix types.
 * - numeric strings are treated as numbers
 * - booleans come after numbers, before strings. false, then true.
 * - non-numeric strings come last
 */


function idValSort(a, b) {
  var bIsNumeric = (0, _fastIsnumeric["default"])(b);

  if ((0, _fastIsnumeric["default"])(a)) {
    if (bIsNumeric) {
      var aN = Number(a);
      var bN = Number(b);
      return aN > bN ? 1 : aN < bN ? -1 : 0;
    }

    return -1;
  }

  if (bIsNumeric) {
    return 1;
  }

  var aIsBool = typeof a === 'boolean';

  if (aIsBool !== (typeof b === 'boolean')) {
    return aIsBool ? -1 : 1;
  }

  return a > b ? 1 : a < b ? -1 : 0;
}
/*
 * Provide a value known to be before or after v, according to idValSort
 */


var valBefore = function valBefore(v) {
  return (0, _fastIsnumeric["default"])(v) ? v - 1 : 0;
};

var valAfter = function valAfter(v) {
  return typeof v === 'string' ? v + 'z' : 'z';
};

function addMap(depMap, id, prop, dependency) {
  var idMap = depMap[id] = depMap[id] || {};
  var callbacks = idMap[prop] = idMap[prop] || [];
  callbacks.push(dependency);
}

function addPattern(depMap, idSpec, prop, dependency) {
  var keys = Object.keys(idSpec).sort();
  var keyStr = keys.join(',');
  var values = (0, _ramda.props)(keys, idSpec);
  var keyCallbacks = depMap[keyStr] = depMap[keyStr] || {};
  var propCallbacks = keyCallbacks[prop] = keyCallbacks[prop] || [];
  var valMatch = false;

  for (var i = 0; i < propCallbacks.length; i++) {
    if ((0, _ramda.equals)(values, propCallbacks[i].values)) {
      valMatch = propCallbacks[i];
      break;
    }
  }

  if (!valMatch) {
    valMatch = {
      keys: keys,
      values: values,
      callbacks: []
    };
    propCallbacks.push(valMatch);
  }

  valMatch.callbacks.push(dependency);
}

function validateDependencies(parsedDependencies, dispatchError) {
  var outStrs = {};
  var outObjs = [];
  parsedDependencies.forEach(function (dep) {
    var inputs = dep.inputs,
        outputs = dep.outputs,
        state = dep.state;
    var hasOutputs = true;

    if (outputs.length === 1 && !outputs[0].id && !outputs[0].property) {
      hasOutputs = false;
      dispatchError('A callback is missing Outputs', ['Please provide an output for this callback:', JSON.stringify(dep, null, 2)]);
    }

    var head = 'In the callback for output(s):\n  ' + outputs.map(_dependencies_ts.combineIdAndProp).join('\n  ');

    if (!inputs.length) {
      dispatchError('A callback is missing Inputs', [head, 'there are no `Input` elements.', 'Without `Input` elements, it will never get called.', '', 'Subscribing to `Input` components will cause the', 'callback to be called whenever their values change.']);
    }

    var spec = [[outputs, 'Output'], [inputs, 'Input'], [state, 'State']];
    spec.forEach(function (_ref) {
      var _ref2 = _slicedToArray(_ref, 2),
          args = _ref2[0],
          cls = _ref2[1];

      if (cls === 'Output' && !hasOutputs) {
        // just a quirk of how we pass & parse outputs - if you don't
        // provide one, it looks like a single blank output. This is
        // actually useful for graceful failure, so we work around it.
        return;
      }

      if (!Array.isArray(args)) {
        dispatchError("Callback ".concat(cls, "(s) must be an Array"), [head, "For ".concat(cls, "(s) we found:"), JSON.stringify(args), 'but we expected an Array.']);
      }

      args.forEach(function (idProp, i) {
        validateArg(idProp, head, cls, i, dispatchError);
      });
    });
    findDuplicateOutputs(outputs, head, dispatchError, outStrs, outObjs);
    findInOutOverlap(outputs, inputs, head, dispatchError);
    findMismatchedWildcards(outputs, inputs, state, head, dispatchError);
  });
}

function validateArg(_ref3, head, cls, i, dispatchError) {
  var id = _ref3.id,
      property = _ref3.property;

  if (typeof property !== 'string' || !property) {
    dispatchError('Callback property error', [head, "".concat(cls, "[").concat(i, "].property = ").concat(JSON.stringify(property)), 'but we expected `property` to be a non-empty string.']);
  }

  if (_typeof(id) === 'object') {
    if ((0, _ramda.isEmpty)(id)) {
      dispatchError('Callback item missing ID', [head, "".concat(cls, "[").concat(i, "].id = {}"), 'Every item linked to a callback needs an ID']);
    }

    (0, _ramda.forEachObjIndexed)(function (v, k) {
      if (!k) {
        dispatchError('Callback wildcard ID error', [head, "".concat(cls, "[").concat(i, "].id has key \"").concat(k, "\""), 'Keys must be non-empty strings.']);
      }

      if (_typeof(v) === 'object' && v.wild) {
        if (allowedWildcards[cls][v.wild] !== v) {
          dispatchError('Callback wildcard ID error', [head, "".concat(cls, "[").concat(i, "].id[\"").concat(k, "\"] = ").concat(v.wild), "Allowed wildcards for ".concat(cls, "s are:"), (0, _ramda.keys)(allowedWildcards[cls]).join(', ')]);
        }
      } else if (!(0, _ramda.includes)(_typeof(v), wildcardValTypes)) {
        dispatchError('Callback wildcard ID error', [head, "".concat(cls, "[").concat(i, "].id[\"").concat(k, "\"] = ").concat(JSON.stringify(v)), 'Wildcard callback ID values must be either wildcards', 'or constants of one of these types:', wildcardValTypes.join(', ')]);
      }
    }, id);
  } else if (typeof id === 'string') {
    if (!id) {
      dispatchError('Callback item missing ID', [head, "".concat(cls, "[").concat(i, "].id = \"").concat(id, "\""), 'Every item linked to a callback needs an ID']);
    }

    var invalidChars = idInvalidChars.filter(function (c) {
      return (0, _ramda.includes)(c, id);
    });

    if (invalidChars.length) {
      dispatchError('Callback invalid ID string', [head, "".concat(cls, "[").concat(i, "].id = '").concat(id, "'"), "characters '".concat(invalidChars.join("', '"), "' are not allowed.")]);
    }
  } else {
    dispatchError('Callback ID type error', [head, "".concat(cls, "[").concat(i, "].id = ").concat(JSON.stringify(id)), 'IDs must be strings or wildcard-compatible objects.']);
  }
}

function findDuplicateOutputs(outputs, head, dispatchError, outStrs, outObjs) {
  var newOutputStrs = {};
  var newOutputObjs = [];
  outputs.forEach(function (_ref4, i) {
    var id = _ref4.id,
        property = _ref4.property;

    if (typeof id === 'string') {
      var idProp = (0, _dependencies_ts.combineIdAndProp)({
        id: id,
        property: property
      });

      if (newOutputStrs[idProp]) {
        dispatchError('Duplicate callback Outputs', [head, "Output ".concat(i, " (").concat(idProp, ") is already used by this callback.")]);
      } else if (outStrs[idProp]) {
        dispatchError('Duplicate callback outputs', [head, "Output ".concat(i, " (").concat(idProp, ") is already in use."), 'Any given output can only have one callback that sets it.', 'To resolve this situation, try combining these into', 'one callback function, distinguishing the trigger', 'by using `dash.callback_context` if necessary.']);
      } else {
        newOutputStrs[idProp] = 1;
      }
    } else {
      var idObj = {
        id: id,
        property: property
      };
      var selfOverlap = wildcardOverlap(idObj, newOutputObjs);
      var otherOverlap = selfOverlap || wildcardOverlap(idObj, outObjs);

      if (selfOverlap || otherOverlap) {
        var _idProp = (0, _dependencies_ts.combineIdAndProp)(idObj);

        var idProp2 = (0, _dependencies_ts.combineIdAndProp)(selfOverlap || otherOverlap);
        dispatchError('Overlapping wildcard callback outputs', [head, "Output ".concat(i, " (").concat(_idProp, ")"), "overlaps another output (".concat(idProp2, ")"), "used in ".concat(selfOverlap ? 'this' : 'a different', " callback.")]);
      } else {
        newOutputObjs.push(idObj);
      }
    }
  });
  (0, _ramda.keys)(newOutputStrs).forEach(function (k) {
    outStrs[k] = 1;
  });
  newOutputObjs.forEach(function (idObj) {
    outObjs.push(idObj);
  });
}

function findInOutOverlap(outputs, inputs, head, dispatchError) {
  outputs.forEach(function (out, outi) {
    var outId = out.id,
        outProp = out.property;
    inputs.forEach(function (in_, ini) {
      var inId = in_.id,
          inProp = in_.property;

      if (outProp !== inProp || _typeof(outId) !== _typeof(inId)) {
        return;
      }

      if (typeof outId === 'string') {
        if (outId === inId) {
          dispatchError('Same `Input` and `Output`', [head, "Input ".concat(ini, " (").concat((0, _dependencies_ts.combineIdAndProp)(in_), ")"), "matches Output ".concat(outi, " (").concat((0, _dependencies_ts.combineIdAndProp)(out), ")")]);
        }
      } else if (wildcardOverlap(in_, [out])) {
        dispatchError('Same `Input` and `Output`', [head, "Input ".concat(ini, " (").concat((0, _dependencies_ts.combineIdAndProp)(in_), ")"), 'can match the same component(s) as', "Output ".concat(outi, " (").concat((0, _dependencies_ts.combineIdAndProp)(out), ")")]);
      }
    });
  });
}

function findMismatchedWildcards(outputs, inputs, state, head, dispatchError) {
  var _findWildcardKeys = findWildcardKeys(outputs[0].id),
      out0MatchKeys = _findWildcardKeys.matchKeys;

  outputs.forEach(function (out, i) {
    if (i && !(0, _ramda.equals)(findWildcardKeys(out.id).matchKeys, out0MatchKeys)) {
      dispatchError('Mismatched `MATCH` wildcards across `Output`s', [head, "Output ".concat(i, " (").concat((0, _dependencies_ts.combineIdAndProp)(out), ")"), 'does not have MATCH wildcards on the same keys as', "Output 0 (".concat((0, _dependencies_ts.combineIdAndProp)(outputs[0]), ")."), 'MATCH wildcards must be on the same keys for all Outputs.', 'ALL wildcards need not match, only MATCH.']);
    }
  });
  [[inputs, 'Input'], [state, 'State']].forEach(function (_ref5) {
    var _ref6 = _slicedToArray(_ref5, 2),
        args = _ref6[0],
        cls = _ref6[1];

    args.forEach(function (arg, i) {
      var _findWildcardKeys2 = findWildcardKeys(arg.id),
          matchKeys = _findWildcardKeys2.matchKeys,
          allsmallerKeys = _findWildcardKeys2.allsmallerKeys;

      var allWildcardKeys = matchKeys.concat(allsmallerKeys);
      var diff = (0, _ramda.difference)(allWildcardKeys, out0MatchKeys);

      if (diff.length) {
        diff.sort();
        dispatchError('`Input` / `State` wildcards not in `Output`s', [head, "".concat(cls, " ").concat(i, " (").concat((0, _dependencies_ts.combineIdAndProp)(arg), ")"), "has MATCH or ALLSMALLER on key(s) ".concat(diff.join(', ')), "where Output 0 (".concat((0, _dependencies_ts.combineIdAndProp)(outputs[0]), ")"), 'does not have a MATCH wildcard. Inputs and State do not', 'need every MATCH from the Output(s), but they cannot have', 'extras beyond the Output(s).']);
      }
    });
  });
}

var matchWildKeys = function matchWildKeys(_ref7) {
  var _ref8 = _slicedToArray(_ref7, 2),
      a = _ref8[0],
      b = _ref8[1];

  var aWild = a && a.wild;
  var bWild = b && b.wild;

  if (aWild && bWild) {
    // Every wildcard combination overlaps except MATCH<->ALLSMALLER
    return !(a === MATCH && b === ALLSMALLER || a === ALLSMALLER && b === MATCH);
  }

  return a === b || aWild || bWild;
};

function wildcardOverlap(_ref9, objs) {
  var id = _ref9.id,
      property = _ref9.property;
  var idKeys = (0, _ramda.keys)(id).sort();
  var idVals = (0, _ramda.props)(idKeys, id);

  var _iterator = _createForOfIteratorHelper(objs),
      _step;

  try {
    for (_iterator.s(); !(_step = _iterator.n()).done;) {
      var obj = _step.value;
      var id2 = obj.id,
          property2 = obj.property;

      if (property2 === property && typeof id2 !== 'string' && (0, _ramda.equals)((0, _ramda.keys)(id2).sort(), idKeys) && (0, _ramda.all)(matchWildKeys, (0, _ramda.zip)(idVals, (0, _ramda.props)(idKeys, id2)))) {
        return obj;
      }
    }
  } catch (err) {
    _iterator.e(err);
  } finally {
    _iterator.f();
  }

  return false;
}

function validateCallbacksToLayout(state_, dispatchError) {
  var config = state_.config,
      graphs = state_.graphs,
      layout_ = state_.layout,
      paths_ = state_.paths;
  var validateIds = !config.suppress_callback_exceptions;
  var layout, paths;

  if (validateIds && config.validation_layout) {
    layout = config.validation_layout;
    paths = (0, _paths.computePaths)(layout, [], null, paths_.events);
  } else {
    layout = layout_;
    paths = paths_;
  }

  var outputMap = graphs.outputMap,
      inputMap = graphs.inputMap,
      outputPatterns = graphs.outputPatterns,
      inputPatterns = graphs.inputPatterns;

  function tail(callbacks) {
    return 'This ID was used in the callback(s) for Output(s):\n  ' + callbacks.map(function (_ref10) {
      var outputs = _ref10.outputs;
      return outputs.map(_dependencies_ts.combineIdAndProp).join(', ');
    }).join('\n  ');
  }

  function missingId(id, cls, callbacks) {
    dispatchError('ID not found in layout', ["Attempting to connect a callback ".concat(cls, " item to component:"), "  \"".concat(stringifyId(id), "\""), 'but no components with that id exist in the layout.', '', 'If you are assigning callbacks to components that are', 'generated by other callbacks (and therefore not in the', 'initial layout), you can suppress this exception by setting', '`suppress_callback_exceptions=True`.', tail(callbacks)]);
  }

  function validateProp(id, idPath, prop, cls, callbacks) {
    var component = (0, _ramda.path)(idPath, layout);

    var element = _registry["default"].resolve(component); // note: Flow components do not have propTypes, so we can't validate.


    if (element && element.propTypes && !element.propTypes[prop]) {
      // look for wildcard props (ie data-* etc)
      for (var propName in element.propTypes) {
        var last = propName.length - 1;

        if (propName.charAt(last) === '*' && prop.substr(0, last) === propName.substr(0, last)) {
          return;
        }
      }

      var type = component.type,
          namespace = component.namespace;
      dispatchError('Invalid prop for this component', ["Property \"".concat(prop, "\" was used with component ID:"), "  ".concat(JSON.stringify(id)), "in one of the ".concat(cls, " items of a callback."), "This ID is assigned to a ".concat(namespace, ".").concat(type, " component"), 'in the layout, which does not support this property.', tail(callbacks)]);
    }
  }

  function validateIdPatternProp(id, property, cls, callbacks) {
    (0, _dependencies_ts.resolveDeps)()(paths)({
      id: id,
      property: property
    }).forEach(function (dep) {
      var idResolved = dep.id,
          idPath = dep.path;
      validateProp(idResolved, idPath, property, cls, callbacks);
    });
  }

  var callbackIdsCheckedForState = {};

  function validateState(callback) {
    var state = callback.state,
        output = callback.output; // ensure we don't check the same callback for state multiple times

    if (callbackIdsCheckedForState[output]) {
      return;
    }

    callbackIdsCheckedForState[output] = 1;
    var cls = 'State';
    state.forEach(function (_ref11) {
      var id = _ref11.id,
          property = _ref11.property;

      if (typeof id === 'string') {
        var idPath = (0, _paths.getPath)(paths, id);

        if (!idPath) {
          if (validateIds) {
            missingId(id, cls, [callback]);
          }
        } else {
          validateProp(id, idPath, property, cls, [callback]);
        }
      } // Only validate props for State object ids that we don't need to
      // resolve them to specific inputs or outputs
      else if (!(0, _ramda.intersection)([MATCH, ALLSMALLER], (0, _ramda.values)(id)).length) {
          validateIdPatternProp(id, property, cls, [callback]);
        }
    });
  }

  function validateMap(map, cls, doState) {
    for (var id in map) {
      var idProps = map[id];
      var idPath = (0, _paths.getPath)(paths, id);

      if (!idPath) {
        if (validateIds) {
          missingId(id, cls, (0, _ramda.flatten)((0, _ramda.values)(idProps)));
        }
      } else {
        for (var property in idProps) {
          var callbacks = idProps[property];
          validateProp(id, idPath, property, cls, callbacks);

          if (doState) {
            // It would be redundant to check state on both inputs
            // and outputs - so only set doState for outputs.
            callbacks.forEach(validateState);
          }
        }
      }
    }
  }

  validateMap(outputMap, 'Output', true);
  validateMap(inputMap, 'Input');

  function validatePatterns(patterns, cls, doState) {
    for (var keyStr in patterns) {
      var keyPatterns = patterns[keyStr];

      var _loop = function _loop(property) {
        keyPatterns[property].forEach(function (_ref12) {
          var keys = _ref12.keys,
              values = _ref12.values,
              callbacks = _ref12.callbacks;
          var id = (0, _ramda.zipObj)(keys, values);
          validateIdPatternProp(id, property, cls, callbacks);

          if (doState) {
            callbacks.forEach(validateState);
          }
        });
      };

      for (var property in keyPatterns) {
        _loop(property);
      }
    }
  }

  validatePatterns(outputPatterns, 'Output', true);
  validatePatterns(inputPatterns, 'Input');
}

function computeGraphs(dependencies, dispatchError) {
  // multiGraph is just for finding circular deps
  var multiGraph = new _dependencyGraph.DepGraph();
  var wildcardPlaceholders = {};
  var fixIds = (0, _ramda.map)((0, _ramda.evolve)({
    id: parseIfWildcard
  }));
  var parsedDependencies = (0, _ramda.map)(function (dep) {
    var output = dep.output;
    var out = (0, _ramda.evolve)({
      inputs: fixIds,
      state: fixIds
    }, dep);
    out.outputs = (0, _ramda.map)(function (outi) {
      return (0, _ramda.assoc)('out', true, splitIdAndProp(outi));
    }, isMultiOutputProp(output) ? parseMultipleOutputs(output) : [output]);
    return out;
  }, dependencies);
  var hasError = false;

  var wrappedDE = function wrappedDE(message, lines) {
    hasError = true;
    dispatchError(message, lines);
  };

  validateDependencies(parsedDependencies, wrappedDE);
  /*
   * For regular ids, outputMap and inputMap are:
   *   {[id]: {[prop]: [callback, ...]}}
   * where callbacks are the matching specs from the original
   * dependenciesRequest, but with outputs parsed to look like inputs,
   * and a list matchKeys added if the outputs have MATCH wildcards.
   * For outputMap there should only ever be one callback per id/prop
   * but for inputMap there may be many.
   *
   * For wildcard ids, outputPatterns and inputPatterns are:
   *   {
   *       [keystr]: {
   *           [prop]: [
   *               {keys: [...], values: [...], callbacks: [callback, ...]},
   *               {...}
   *           ]
   *       }
   *   }
   * keystr is a stringified ordered list of keys in the id
   * keys is the same ordered list (just copied for convenience)
   * values is an array of explicit or wildcard values for each key in keys
   */

  var outputMap = {};
  var inputMap = {};
  var outputPatterns = {};
  var inputPatterns = {};
  var finalGraphs = {
    MultiGraph: multiGraph,
    outputMap: outputMap,
    inputMap: inputMap,
    outputPatterns: outputPatterns,
    inputPatterns: inputPatterns,
    callbacks: parsedDependencies
  };

  if (hasError) {
    // leave the graphs empty if we found an error, so we don't try to
    // execute the broken callbacks.
    return finalGraphs;
  }

  parsedDependencies.forEach(function (dependency) {
    var outputs = dependency.outputs,
        inputs = dependency.inputs;
    outputs.concat(inputs).forEach(function (item) {
      var id = item.id;

      if (_typeof(id) === 'object') {
        (0, _ramda.forEachObjIndexed)(function (val, key) {
          if (!wildcardPlaceholders[key]) {
            wildcardPlaceholders[key] = {
              exact: [],
              expand: 0
            };
          }

          var keyPlaceholders = wildcardPlaceholders[key];

          if (val && val.wild) {
            if (val.expand) {
              keyPlaceholders.expand += 1;
            }
          } else if (keyPlaceholders.exact.indexOf(val) === -1) {
            keyPlaceholders.exact.push(val);
          }
        }, id);
      }
    });
  });
  (0, _ramda.forEachObjIndexed)(function (keyPlaceholders) {
    var exact = keyPlaceholders.exact,
        expand = keyPlaceholders.expand;
    var vals = exact.slice().sort(idValSort);

    if (expand) {
      for (var i = 0; i < expand; i++) {
        if (exact.length) {
          vals.splice(0, 0, [valBefore(vals[0])]);
          vals.push(valAfter(vals[vals.length - 1]));
        } else {
          vals.push(i);
        }
      }
    } else if (!exact.length) {
      // only MATCH/ALL - still need a value
      vals.push(0);
    }

    keyPlaceholders.vals = vals;
  }, wildcardPlaceholders);

  function makeAllIds(idSpec, outIdFinal) {
    var idList = [{}];
    (0, _ramda.forEachObjIndexed)(function (val, key) {
      var testVals = wildcardPlaceholders[key].vals;
      var outValIndex = testVals.indexOf(outIdFinal[key]);
      var newVals = [val];

      if (val && val.wild) {
        if (val === ALLSMALLER) {
          if (outValIndex > 0) {
            newVals = testVals.slice(0, outValIndex);
          } else {
            // no smaller items - delete all outputs.
            newVals = [];
          }
        } else {
          // MATCH or ALL
          // MATCH *is* ALL for outputs, ie we don't already have a
          // value specified in `outIdFinal`
          newVals = outValIndex === -1 || val === ALL ? testVals : [outIdFinal[key]];
        }
      } // replicates everything in idList once for each item in
      // newVals, attaching each value at key.


      idList = (0, _ramda.ap)((0, _ramda.ap)([(0, _ramda.assoc)(key)], newVals), idList);
    }, idSpec);
    return idList;
  }

  parsedDependencies.forEach(function registerDependency(dependency) {
    var outputs = dependency.outputs,
        inputs = dependency.inputs; // multiGraph - just for testing circularity

    function addInputToMulti(inIdProp, outIdProp) {
      multiGraph.addNode(inIdProp);
      multiGraph.addDependency(inIdProp, outIdProp);
    }

    function addOutputToMulti(outIdFinal, outIdProp) {
      multiGraph.addNode(outIdProp);
      inputs.forEach(function (inObj) {
        var inId = inObj.id,
            property = inObj.property;

        if (_typeof(inId) === 'object') {
          var inIdList = makeAllIds(inId, outIdFinal);
          inIdList.forEach(function (id) {
            addInputToMulti((0, _dependencies_ts.combineIdAndProp)({
              id: id,
              property: property
            }), outIdProp);
          });
        } else {
          addInputToMulti((0, _dependencies_ts.combineIdAndProp)(inObj), outIdProp);
        }
      });
    } // We'll continue to use dep.output as its id, but add outputs as well
    // for convenience and symmetry with the structure of inputs and state.
    // Also collect MATCH keys in the output (all outputs must share these)
    // and ALL keys in the first output (need not be shared but we'll use
    // the first output for calculations) for later convenience.


    var _findWildcardKeys3 = findWildcardKeys(outputs[0].id),
        matchKeys = _findWildcardKeys3.matchKeys;

    var firstSingleOutput = (0, _ramda.findIndex)(function (o) {
      return !isMultiValued(o.id);
    }, outputs);
    var finalDependency = (0, _ramda.mergeRight)({
      matchKeys: matchKeys,
      firstSingleOutput: firstSingleOutput,
      outputs: outputs
    }, dependency);
    outputs.forEach(function (outIdProp) {
      var outId = outIdProp.id,
          property = outIdProp.property;

      if (_typeof(outId) === 'object') {
        var outIdList = makeAllIds(outId, {});
        outIdList.forEach(function (id) {
          addOutputToMulti(id, (0, _dependencies_ts.combineIdAndProp)({
            id: id,
            property: property
          }));
        });
        addPattern(outputPatterns, outId, property, finalDependency);
      } else {
        addOutputToMulti({}, (0, _dependencies_ts.combineIdAndProp)(outIdProp));
        addMap(outputMap, outId, property, finalDependency);
      }
    });
    inputs.forEach(function (inputObject) {
      var inId = inputObject.id,
          inProp = inputObject.property;

      if (_typeof(inId) === 'object') {
        addPattern(inputPatterns, inId, inProp, finalDependency);
      } else {
        addMap(inputMap, inId, inProp, finalDependency);
      }
    });
  });
  return finalGraphs;
}

function findWildcardKeys(id) {
  var matchKeys = [];
  var allsmallerKeys = [];

  if (_typeof(id) === 'object') {
    (0, _ramda.forEachObjIndexed)(function (val, key) {
      if (val === MATCH) {
        matchKeys.push(key);
      } else if (val === ALLSMALLER) {
        allsmallerKeys.push(key);
      }
    }, id);
    matchKeys.sort();
    allsmallerKeys.sort();
  }

  return {
    matchKeys: matchKeys,
    allsmallerKeys: allsmallerKeys
  };
}
/*
 * Do the given id values `vals` match the pattern `patternVals`?
 * `keys`, `patternVals`, and `vals` are all arrays, and we already know that
 * we're only looking at ids with the same keys as the pattern.
 *
 * Optionally, include another reference set of the same - to ensure the
 * correct matching of MATCH or ALLSMALLER between input and output items.
 */


function idMatch(keys, vals, patternVals, refKeys, refVals, refPatternVals) {
  for (var i = 0; i < keys.length; i++) {
    var val = vals[i];
    var patternVal = patternVals[i];

    if (patternVal.wild) {
      // If we have a second id, compare the wildcard values.
      // Without a second id, all wildcards pass at this stage.
      if (refKeys && patternVal !== ALL) {
        var refIndex = refKeys.indexOf(keys[i]);
        var refPatternVal = refPatternVals[refIndex]; // Sanity check. Shouldn't ever fail this, if the back end
        // did its job validating callbacks.
        // You can't resolve an input against an input, because
        // two ALLSMALLER's wouldn't make sense!

        if (patternVal === ALLSMALLER && refPatternVal === ALLSMALLER) {
          throw new Error('invalid wildcard id pair: ' + JSON.stringify({
            keys: keys,
            patternVals: patternVals,
            vals: vals,
            refKeys: refKeys,
            refPatternVals: refPatternVals,
            refVals: refVals
          }));
        }

        if (idValSort(val, refVals[refIndex]) !== (patternVal === ALLSMALLER ? -1 : refPatternVal === ALLSMALLER ? 1 : 0)) {
          return false;
        }
      }
    } else if (val !== patternVal) {
      return false;
    }
  }

  return true;
}

function getAnyVals(patternVals, vals) {
  var matches = [];

  for (var i = 0; i < patternVals.length; i++) {
    if (patternVals[i] === MATCH) {
      matches.push(vals[i]);
    }
  }

  return matches.length ? JSON.stringify(matches) : '';
}
/*
 * Does this item (input / output / state) support multiple values?
 * string IDs do not; wildcard IDs only do if they contain ALL or ALLSMALLER
 */


function isMultiValued(_ref13) {
  var id = _ref13.id;
  return _typeof(id) === 'object' && (0, _ramda.any)(function (v) {
    return v.multi;
  }, (0, _ramda.values)(id));
}
/*
 * For a given output id and prop, find the callback generating it.
 * If no callback is found, returns false.
 * If one is found, returns:
 * {
 *     callback: the callback spec {outputs, inputs, state etc}
 *     anyVals: stringified list of resolved MATCH keys we matched
 *     resolvedId: the "outputs" id string plus MATCH values we matched
 *     getOutputs: accessor function to give all resolved outputs of this
 *         callback. Takes `paths` as argument to apply when the callback is
 *         dispatched, in case a previous callback has altered the layout.
 *         The result is a list of {id (string or object), property (string)}
 *     getInputs: same for inputs
 *     getState: same for state
 *     changedPropIds: an object of {[idAndProp]: v} triggering this callback
 *         v = DIRECT (2): the prop was changed in the front end, so dependent
 *             callbacks *MUST* be executed.
 *         v = INDIRECT (1): the prop is expected to be changed by a callback,
 *             but if this is prevented, dependent callbacks may be pruned.
 *     initialCall: boolean, if true we don't require any changedPropIds
 *         to keep this callback around, as it's the initial call to populate
 *         this value on page load or changing part of the layout.
 *         By default this is true for callbacks generated by
 *         getCallbackByOutput, false from getCallbacksByInput.
 * }
 */


function getCallbackByOutput(graphs, paths, id, prop) {
  var resolve;
  var callback;
  var anyVals = '';

  if (typeof id === 'string') {
    // standard id version
    var callbacks = (graphs.outputMap[id] || {})[prop];

    if (callbacks) {
      callback = callbacks[0];
      resolve = (0, _dependencies_ts.resolveDeps)();
    }
  } else {
    // wildcard version
    var _keys = Object.keys(id).sort();

    var vals = (0, _ramda.props)(_keys, id);

    var keyStr = _keys.join(',');

    var patterns = (graphs.outputPatterns[keyStr] || {})[prop];

    if (patterns) {
      for (var i = 0; i < patterns.length; i++) {
        var patternVals = patterns[i].values;

        if (idMatch(_keys, vals, patternVals)) {
          callback = patterns[i].callbacks[0];
          resolve = (0, _dependencies_ts.resolveDeps)(_keys, vals, patternVals);
          anyVals = getAnyVals(patternVals, vals);
          break;
        }
      }
    }
  }

  if (!resolve) {
    return false;
  }

  return (0, _dependencies_ts.makeResolvedCallback)(callback, resolve, anyVals);
}

function addResolvedFromOutputs(callback, outPattern, outs, matches) {
  var out0Keys = Object.keys(outPattern.id).sort();
  var out0PatternVals = (0, _ramda.props)(out0Keys, outPattern.id);
  outs.forEach(function (_ref14) {
    var outId = _ref14.id;
    var outVals = (0, _ramda.props)(out0Keys, outId);
    matches.push((0, _dependencies_ts.makeResolvedCallback)(callback, (0, _dependencies_ts.resolveDeps)(out0Keys, outVals, out0PatternVals), getAnyVals(out0PatternVals, outVals)));
  });
}

function addAllResolvedFromOutputs(resolve, paths, matches) {
  return function (callback) {
    var matchKeys = callback.matchKeys,
        firstSingleOutput = callback.firstSingleOutput,
        outputs = callback.outputs;

    if (matchKeys.length) {
      var singleOutPattern = outputs[firstSingleOutput];

      if (singleOutPattern) {
        addResolvedFromOutputs(callback, singleOutPattern, resolve(paths)(singleOutPattern), matches);
      } else {
        /*
         * If every output has ALL we need to reduce resolved set
         * to one item per combination of MATCH values.
         * That will give one result per callback invocation.
         */
        var anySeen = {};
        outputs.forEach(function (outPattern) {
          var outSet = resolve(paths)(outPattern).filter(function (i) {
            var matchStr = JSON.stringify((0, _ramda.props)(matchKeys, i.id));

            if (!anySeen[matchStr]) {
              anySeen[matchStr] = 1;
              return true;
            }

            return false;
          });
          addResolvedFromOutputs(callback, outPattern, outSet, matches);
        });
      }
    } else {
      var cb = (0, _dependencies_ts.makeResolvedCallback)(callback, resolve, '');

      if ((0, _ramda.flatten)(cb.getOutputs(paths)).length) {
        matches.push(cb);
      }
    }
  };
}
/*
 * For a given id and prop find all callbacks it's an input of.
 *
 * Returns an array of objects:
 *   {callback, resolvedId, getOutputs, getInputs, getState}
 *   See getCallbackByOutput for details.
 *
 * Note that if the original input contains an ALLSMALLER wildcard,
 * there may be many entries for the same callback, but any given output
 * (with an MATCH corresponding to the input's ALLSMALLER) will only appear
 * in one entry.
 */


function getWatchedKeys(id, newProps, graphs) {
  if (!(id && graphs && newProps.length)) {
    return [];
  }

  if (typeof id === 'string') {
    var inputs = graphs.inputMap[id];
    return inputs ? newProps.filter(function (newProp) {
      return inputs[newProp];
    }) : [];
  }

  var keys = Object.keys(id).sort();
  var vals = (0, _ramda.props)(keys, id);
  var keyStr = keys.join(',');
  var keyPatterns = graphs.inputPatterns[keyStr];

  if (!keyPatterns) {
    return [];
  }

  return newProps.filter(function (prop) {
    var patterns = keyPatterns[prop];
    return patterns && patterns.some(function (pattern) {
      return idMatch(keys, vals, pattern.values);
    });
  });
}
/*
 * Return a list of all callbacks referencing a chunk of the layout,
 * either as inputs or outputs.
 *
 * opts.outputsOnly: boolean, set true when crawling the *whole* layout,
 *   because outputs are enough to get everything.
 * opts.removedArrayInputsOnly: boolean, set true to only look for inputs in
 *   wildcard arrays (ALL or ALLSMALLER), no outputs. This gets used to tell
 *   when the new *absence* of a given component should trigger a callback.
 * opts.newPaths: paths object after the edit - to be used with
 *   removedArrayInputsOnly to determine if the callback still has its outputs
 * opts.chunkPath: path to the new chunk - used to determine if any outputs are
 *   outside of this chunk, because this determines whether inputs inside the
 *   chunk count as having changed
 *
 * Returns an array of objects:
 *   {callback, resolvedId, getOutputs, getInputs, getState, ...etc}
 *   See getCallbackByOutput for details.
 */


function getUnfilteredLayoutCallbacks(graphs, paths, layoutChunk, opts) {
  var outputsOnly = opts.outputsOnly,
      removedArrayInputsOnly = opts.removedArrayInputsOnly,
      newPaths = opts.newPaths,
      chunkPath = opts.chunkPath;
  var foundCbIds = {};
  var callbacks = [];

  function addCallback(callback) {
    if (callback) {
      var foundIndex = foundCbIds[callback.resolvedId];

      if (foundIndex !== undefined) {
        var foundCb = callbacks[foundIndex];
        foundCb.changedPropIds = (0, _dependencies_ts.mergeMax)(foundCb.changedPropIds, callback.changedPropIds);

        if (callback.initialCall) {
          foundCb.initialCall = true;
        }
      } else {
        foundCbIds[callback.resolvedId] = callbacks.length;
        callbacks.push(callback);
      }
    }
  }

  function addCallbackIfArray(idStr) {
    return function (cb) {
      return cb.getInputs(paths).some(function (ini) {
        if (Array.isArray(ini) && ini.some(function (inij) {
          return stringifyId(inij.id) === idStr;
        })) {
          // This callback should trigger even with no changedProps,
          // since the props that changed no longer exist.
          // We're kind of abusing the `initialCall` flag here, it's
          // more like a "final call" for the removed inputs, but
          // this case is not subject to `prevent_initial_call`.
          if ((0, _ramda.flatten)(cb.getOutputs(newPaths)).length) {
            cb.initialCall = true;
            cb.changedPropIds = {};
            addCallback(cb);
          }

          return true;
        }

        return false;
      });
    };
  }

  function handleOneId(id, outIdCallbacks, inIdCallbacks) {
    if (outIdCallbacks) {
      for (var property in outIdCallbacks) {
        var cb = getCallbackByOutput(graphs, paths, id, property);

        if (cb) {
          // callbacks found in the layout by output should always run
          // unless specifically requested not to.
          // ie this is the initial call of this callback even if it's
          // not the page initialization but just a new layout chunk
          if (!cb.callback.prevent_initial_call) {
            cb.initialCall = true;
            addCallback(cb);
          }
        }
      }
    }

    if (!outputsOnly && inIdCallbacks) {
      var maybeAddCallback = removedArrayInputsOnly ? addCallbackIfArray(stringifyId(id)) : addCallback;
      var handleThisCallback = maybeAddCallback;

      if (chunkPath) {
        handleThisCallback = function handleThisCallback(cb) {
          if (!(0, _ramda.all)((0, _ramda.startsWith)(chunkPath), (0, _ramda.pluck)('path', (0, _ramda.flatten)(cb.getOutputs(paths))))) {
            maybeAddCallback(cb);
          }
        };
      }

      for (var _property in inIdCallbacks) {
        (0, _dependencies_ts.getCallbacksByInput)(graphs, paths, id, _property, _dependencies_ts.INDIRECT).forEach(handleThisCallback);
      }
    }
  }

  (0, _utils.crawlLayout)(layoutChunk, function (child) {
    var id = (0, _ramda.path)(['props', 'id'], child);

    if (id) {
      if (typeof id === 'string' && !removedArrayInputsOnly) {
        handleOneId(id, graphs.outputMap[id], graphs.inputMap[id]);
      } else {
        var keyStr = Object.keys(id).sort().join(',');
        handleOneId(id, !removedArrayInputsOnly && graphs.outputPatterns[keyStr], graphs.inputPatterns[keyStr]);
      }
    }
  });
  return (0, _ramda.map)(function (cb) {
    return _objectSpread(_objectSpread({}, cb), {}, {
      priority: (0, _dependencies_ts.getPriority)(graphs, paths, cb)
    });
  }, callbacks);
}