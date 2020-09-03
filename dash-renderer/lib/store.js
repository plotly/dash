"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _ramda = require("ramda");

var _redux = require("redux");

var _reduxThunk = _interopRequireDefault(require("redux-thunk"));

var _reducer = require("./reducers/reducer");

var _StoreObserver = _interopRequireDefault(require("./StoreObserver"));

var _documentTitle = _interopRequireDefault(require("./observers/documentTitle"));

var _executedCallbacks = _interopRequireDefault(require("./observers/executedCallbacks"));

var _executingCallbacks = _interopRequireDefault(require("./observers/executingCallbacks"));

var _isLoading = _interopRequireDefault(require("./observers/isLoading"));

var _loadingMap = _interopRequireDefault(require("./observers/loadingMap"));

var _prioritizedCallbacks = _interopRequireDefault(require("./observers/prioritizedCallbacks"));

var _requestedCallbacks = _interopRequireDefault(require("./observers/requestedCallbacks"));

var _storedCallbacks = _interopRequireDefault(require("./observers/storedCallbacks"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

var store;
var storeObserver = new _StoreObserver["default"]();
var setObservers = (0, _ramda.once)(function () {
  var observe = storeObserver.observe;
  observe(_documentTitle["default"]);
  observe(_isLoading["default"]);
  observe(_loadingMap["default"]);
  observe(_requestedCallbacks["default"]);
  observe(_prioritizedCallbacks["default"]);
  observe(_executingCallbacks["default"]);
  observe(_executedCallbacks["default"]);
  observe(_storedCallbacks["default"]);
});

function createAppStore(reducer, middleware) {
  store = (0, _redux.createStore)(reducer, middleware);
  storeObserver.setStore(store);
  setObservers();
}
/**
 * Initialize a Redux store with thunk, plus logging (only in development mode) middleware
 *
 * @param {bool} reset: discard any previous store
 *
 * @returns {Store<GenericStoreEnhancer>}
 *  An initialized redux store with middleware and possible hot reloading of reducers
 */


var initializeStore = function initializeStore(reset) {
  if (store && !reset) {
    return store;
  }

  var reducer = (0, _reducer.createReducer)(); // eslint-disable-next-line no-process-env

  if (process.env.NODE_ENV === 'production') {
    createAppStore(reducer, (0, _redux.applyMiddleware)(_reduxThunk["default"]));
  } else {
    // only attach logger to middleware in non-production mode
    var reduxDTEC = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__;

    if (reduxDTEC) {
      createAppStore(reducer, reduxDTEC((0, _redux.applyMiddleware)(_reduxThunk["default"])));
    } else {
      createAppStore(reducer, (0, _redux.applyMiddleware)(_reduxThunk["default"]));
    }
  }

  if (!reset) {
    // TODO - Protect this under a debug mode?
    window.store = store;
  }

  if (module.hot) {
    // Enable hot module replacement for reducers
    module.hot.accept('./reducers/reducer', function () {
      var nextRootReducer = require('./reducers/reducer').createReducer();

      store.replaceReducer(nextRootReducer);
    });
  }

  return store;
};

var _default = initializeStore;
exports["default"] = _default;