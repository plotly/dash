"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = exports.CallbackAggregateActionType = exports.CallbackActionType = void 0;

var _ramda = require("ramda");

var _transforms, _fields;

function ownKeys(object, enumerableOnly) { var keys = Object.keys(object); if (Object.getOwnPropertySymbols) { var symbols = Object.getOwnPropertySymbols(object); if (enumerableOnly) symbols = symbols.filter(function (sym) { return Object.getOwnPropertyDescriptor(object, sym).enumerable; }); keys.push.apply(keys, symbols); } return keys; }

function _objectSpread(target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i] != null ? arguments[i] : {}; if (i % 2) { ownKeys(Object(source), true).forEach(function (key) { _defineProperty(target, key, source[key]); }); } else if (Object.getOwnPropertyDescriptors) { Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)); } else { ownKeys(Object(source)).forEach(function (key) { Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key)); }); } } return target; }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

var CallbackActionType;
exports.CallbackActionType = CallbackActionType;

(function (CallbackActionType) {
  CallbackActionType["AddBlocked"] = "Callbacks.AddBlocked";
  CallbackActionType["AddExecuted"] = "Callbacks.AddExecuted";
  CallbackActionType["AddExecuting"] = "Callbacks.AddExecuting";
  CallbackActionType["AddPrioritized"] = "Callbacks.AddPrioritized";
  CallbackActionType["AddRequested"] = "Callbacks.AddRequested";
  CallbackActionType["AddStored"] = "Callbacks.AddStored";
  CallbackActionType["AddWatched"] = "Callbacks.AddWatched";
  CallbackActionType["RemoveBlocked"] = "Callbacks.RemoveBlocked";
  CallbackActionType["RemoveExecuted"] = "Callbacks.RemoveExecuted";
  CallbackActionType["RemoveExecuting"] = "Callbacks.RemoveExecuting";
  CallbackActionType["RemovePrioritized"] = "Callbacks.ReomvePrioritized";
  CallbackActionType["RemoveRequested"] = "Callbacks.RemoveRequested";
  CallbackActionType["RemoveStored"] = "Callbacks.RemoveStored";
  CallbackActionType["RemoveWatched"] = "Callbacks.RemoveWatched";
})(CallbackActionType || (exports.CallbackActionType = CallbackActionType = {}));

var CallbackAggregateActionType;
exports.CallbackAggregateActionType = CallbackAggregateActionType;

(function (CallbackAggregateActionType) {
  CallbackAggregateActionType["AddCompleted"] = "Callbacks.Completed";
  CallbackAggregateActionType["Aggregate"] = "Callbacks.Aggregate";
})(CallbackAggregateActionType || (exports.CallbackAggregateActionType = CallbackAggregateActionType = {}));

var DEFAULT_STATE = {
  blocked: [],
  executed: [],
  executing: [],
  prioritized: [],
  requested: [],
  stored: [],
  watched: [],
  completed: 0
};
var transforms = (_transforms = {}, _defineProperty(_transforms, CallbackActionType.AddBlocked, _ramda.concat), _defineProperty(_transforms, CallbackActionType.AddExecuted, _ramda.concat), _defineProperty(_transforms, CallbackActionType.AddExecuting, _ramda.concat), _defineProperty(_transforms, CallbackActionType.AddPrioritized, _ramda.concat), _defineProperty(_transforms, CallbackActionType.AddRequested, _ramda.concat), _defineProperty(_transforms, CallbackActionType.AddStored, _ramda.concat), _defineProperty(_transforms, CallbackActionType.AddWatched, _ramda.concat), _defineProperty(_transforms, CallbackActionType.RemoveBlocked, _ramda.difference), _defineProperty(_transforms, CallbackActionType.RemoveExecuted, _ramda.difference), _defineProperty(_transforms, CallbackActionType.RemoveExecuting, _ramda.difference), _defineProperty(_transforms, CallbackActionType.RemovePrioritized, _ramda.difference), _defineProperty(_transforms, CallbackActionType.RemoveRequested, _ramda.difference), _defineProperty(_transforms, CallbackActionType.RemoveStored, _ramda.difference), _defineProperty(_transforms, CallbackActionType.RemoveWatched, _ramda.difference), _transforms);
var fields = (_fields = {}, _defineProperty(_fields, CallbackActionType.AddBlocked, 'blocked'), _defineProperty(_fields, CallbackActionType.AddExecuted, 'executed'), _defineProperty(_fields, CallbackActionType.AddExecuting, 'executing'), _defineProperty(_fields, CallbackActionType.AddPrioritized, 'prioritized'), _defineProperty(_fields, CallbackActionType.AddRequested, 'requested'), _defineProperty(_fields, CallbackActionType.AddStored, 'stored'), _defineProperty(_fields, CallbackActionType.AddWatched, 'watched'), _defineProperty(_fields, CallbackActionType.RemoveBlocked, 'blocked'), _defineProperty(_fields, CallbackActionType.RemoveExecuted, 'executed'), _defineProperty(_fields, CallbackActionType.RemoveExecuting, 'executing'), _defineProperty(_fields, CallbackActionType.RemovePrioritized, 'prioritized'), _defineProperty(_fields, CallbackActionType.RemoveRequested, 'requested'), _defineProperty(_fields, CallbackActionType.RemoveStored, 'stored'), _defineProperty(_fields, CallbackActionType.RemoveWatched, 'watched'), _fields);

var mutateCompleted = function mutateCompleted(state, action) {
  return _objectSpread({}, state, {
    completed: state.completed + action.payload
  });
};

var mutateCallbacks = function mutateCallbacks(state, action) {
  var transform = transforms[action.type];
  var field = fields[action.type];
  return !transform || !field || action.payload.length === 0 ? state : _objectSpread({}, state, _defineProperty({}, field, transform(state[field], action.payload)));
};

var _default = function _default() {
  var state = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : DEFAULT_STATE;
  var action = arguments.length > 1 ? arguments[1] : undefined;
  return (0, _ramda.reduce)(function (s, a) {
    if (a === null) {
      return s;
    } else if (a.type === CallbackAggregateActionType.AddCompleted) {
      return mutateCompleted(s, a);
    } else {
      return mutateCallbacks(s, a);
    }
  }, state, action.type === CallbackAggregateActionType.Aggregate ? action.payload : [action]);
};

exports["default"] = _default;