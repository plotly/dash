"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _redux = require("redux");

var _reduxThunk = _interopRequireDefault(require("redux-thunk"));

var _reducer = require("./reducers/reducer");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

var store;
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
    store = (0, _redux.createStore)(reducer, (0, _redux.applyMiddleware)(_reduxThunk["default"]));
  } else {
    // only attach logger to middleware in non-production mode
    var reduxDTEC = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__;

    if (reduxDTEC) {
      store = (0, _redux.createStore)(reducer, reduxDTEC((0, _redux.applyMiddleware)(_reduxThunk["default"])));
    } else {
      store = (0, _redux.createStore)(reducer, (0, _redux.applyMiddleware)(_reduxThunk["default"]));
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