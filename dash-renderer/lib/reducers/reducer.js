"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.createReducer = createReducer;
exports.apiRequests = void 0;

var _ramda = require("ramda");

var _redux = require("redux");

var _dependencies_ts = require("../actions/dependencies_ts");

var _api = _interopRequireDefault(require("./api"));

var _appLifecycle = _interopRequireDefault(require("./appLifecycle"));

var _callbacks = _interopRequireDefault(require("./callbacks"));

var _config = _interopRequireDefault(require("./config"));

var _dependencyGraph = _interopRequireDefault(require("./dependencyGraph"));

var _error = _interopRequireDefault(require("./error"));

var _history = _interopRequireDefault(require("./history"));

var _hooks = _interopRequireDefault(require("./hooks"));

var _isLoading = _interopRequireDefault(require("./isLoading"));

var _layout = _interopRequireDefault(require("./layout"));

var _loadingMap = _interopRequireDefault(require("./loadingMap"));

var _paths = _interopRequireDefault(require("./paths"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

function _toConsumableArray(arr) { return _arrayWithoutHoles(arr) || _iterableToArray(arr) || _nonIterableSpread(); }

function _nonIterableSpread() { throw new TypeError("Invalid attempt to spread non-iterable instance"); }

function _iterableToArray(iter) { if (Symbol.iterator in Object(iter) || Object.prototype.toString.call(iter) === "[object Arguments]") return Array.from(iter); }

function _arrayWithoutHoles(arr) { if (Array.isArray(arr)) { for (var i = 0, arr2 = new Array(arr.length); i < arr.length; i++) { arr2[i] = arr[i]; } return arr2; } }

var apiRequests = ['dependenciesRequest', 'layoutRequest', 'reloadRequest', 'loginRequest'];
exports.apiRequests = apiRequests;

function mainReducer() {
  var parts = {
    appLifecycle: _appLifecycle["default"],
    callbacks: _callbacks["default"],
    config: _config["default"],
    error: _error["default"],
    graphs: _dependencyGraph["default"],
    history: _history["default"],
    hooks: _hooks["default"],
    isLoading: _isLoading["default"],
    layout: _layout["default"],
    loadingMap: _loadingMap["default"],
    paths: _paths["default"]
  };
  (0, _ramda.forEach)(function (r) {
    parts[r] = (0, _api["default"])(r);
  }, apiRequests);
  return (0, _redux.combineReducers)(parts);
}

function getInputHistoryState(itempath, props, state) {
  var graphs = state.graphs,
      layout = state.layout,
      paths = state.paths;
  var idProps = (0, _ramda.path)(itempath.concat(['props']), layout);

  var _ref = idProps || {},
      id = _ref.id;

  var historyEntry;

  if (id) {
    historyEntry = {
      id: id,
      props: {}
    };
    (0, _ramda.keys)(props).forEach(function (propKey) {
      if ((0, _dependencies_ts.getCallbacksByInput)(graphs, paths, id, propKey).length) {
        historyEntry.props[propKey] = idProps[propKey];
      }
    });
  }

  return historyEntry;
}

function recordHistory(reducer) {
  return function (state, action) {
    // Record initial state
    if (action.type === 'ON_PROP_CHANGE') {
      var _action$payload = action.payload,
          itempath = _action$payload.itempath,
          props = _action$payload.props;
      var historyEntry = getInputHistoryState(itempath, props, state);

      if (historyEntry && !(0, _ramda.isEmpty)(historyEntry.props)) {
        state.history.present = historyEntry;
      }
    }

    var nextState = reducer(state, action);

    if (action.type === 'ON_PROP_CHANGE' && action.payload.source !== 'response') {
      var _action$payload2 = action.payload,
          _itempath = _action$payload2.itempath,
          _props = _action$payload2.props;
      /*
       * if the prop change is an input, then
       * record it so that it can be played back
       */

      var _historyEntry = getInputHistoryState(_itempath, _props, nextState);

      if (_historyEntry && !(0, _ramda.isEmpty)(_historyEntry.props)) {
        nextState.history = {
          past: [].concat(_toConsumableArray(nextState.history.past), [state.history.present]),
          present: _historyEntry,
          future: []
        };
      }
    }

    return nextState;
  };
}

function reloaderReducer(reducer) {
  return function (state, action) {
    var _ref2 = state || {},
        history = _ref2.history,
        config = _ref2.config,
        hooks = _ref2.hooks;

    var newState = state;

    if (action.type === 'RELOAD') {
      newState = {
        history: history,
        config: config,
        hooks: hooks
      };
    } else if (action.type === 'SET_CONFIG') {
      // new config also reloads, and even clears history,
      // in case there's a new user or even a totally different app!
      // hooks are set at an even higher level than config though.
      newState = {
        hooks: hooks
      };
    }

    return reducer(newState, action);
  };
}

function createReducer() {
  return reloaderReducer(recordHistory(mainReducer()));
}