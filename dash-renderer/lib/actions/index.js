"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.hydrateInitialOutputs = hydrateInitialOutputs;
exports.getCSRFHeader = getCSRFHeader;
exports.notifyObservers = notifyObservers;
exports.handleAsyncError = handleAsyncError;
exports.revert = exports.undo = exports.redo = exports.dispatchError = exports.updateProps = exports.setRequestQueue = exports.setPaths = exports.setLayout = exports.setHooks = exports.setGraphs = exports.setConfig = exports.setAppLifecycle = exports.onError = void 0;

var _ramda = require("ramda");

var _reduxActions = require("redux-actions");

var _callbacks = require("./callbacks");

var _constants = require("../reducers/constants");

var _constants2 = require("./constants");

var _cookie = _interopRequireDefault(require("cookie"));

var _dependencies = require("./dependencies");

var _dependencies_ts = require("./dependencies_ts");

var _paths = require("./paths");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function _asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

var onError = (0, _reduxActions.createAction)((0, _constants2.getAction)('ON_ERROR'));
exports.onError = onError;
var setAppLifecycle = (0, _reduxActions.createAction)((0, _constants2.getAction)('SET_APP_LIFECYCLE'));
exports.setAppLifecycle = setAppLifecycle;
var setConfig = (0, _reduxActions.createAction)((0, _constants2.getAction)('SET_CONFIG'));
exports.setConfig = setConfig;
var setGraphs = (0, _reduxActions.createAction)((0, _constants2.getAction)('SET_GRAPHS'));
exports.setGraphs = setGraphs;
var setHooks = (0, _reduxActions.createAction)((0, _constants2.getAction)('SET_HOOKS'));
exports.setHooks = setHooks;
var setLayout = (0, _reduxActions.createAction)((0, _constants2.getAction)('SET_LAYOUT'));
exports.setLayout = setLayout;
var setPaths = (0, _reduxActions.createAction)((0, _constants2.getAction)('SET_PATHS'));
exports.setPaths = setPaths;
var setRequestQueue = (0, _reduxActions.createAction)((0, _constants2.getAction)('SET_REQUEST_QUEUE'));
exports.setRequestQueue = setRequestQueue;
var updateProps = (0, _reduxActions.createAction)((0, _constants2.getAction)('ON_PROP_CHANGE'));
exports.updateProps = updateProps;

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

  dispatch((0, _callbacks.addRequestedCallbacks)((0, _dependencies_ts.getLayoutCallbacks)(graphs, paths, layout, {
    outputsOnly: true
  })));
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
        itempath: (0, _paths.getPath)(paths, id),
        props: props
      }));
      dispatch(notifyObservers({
        id: id,
        props: props
      }));
    }
  };
}

function notifyObservers(_ref2) {
  var id = _ref2.id,
      props = _ref2.props;
  return (/*#__PURE__*/function () {
      var _ref3 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee(dispatch, getState) {
        var _getState3, graphs, paths;

        return regeneratorRuntime.wrap(function _callee$(_context) {
          while (1) {
            switch (_context.prev = _context.next) {
              case 0:
                _getState3 = getState(), graphs = _getState3.graphs, paths = _getState3.paths;
                dispatch((0, _callbacks.addRequestedCallbacks)((0, _dependencies_ts.includeObservers)(id, props, graphs, paths)));

              case 2:
              case "end":
                return _context.stop();
            }
          }
        }, _callee);
      }));

      return function (_x, _x2) {
        return _ref3.apply(this, arguments);
      };
    }()
  );
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