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

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

var RendererStore = /*#__PURE__*/function () {
  function RendererStore() {
    var _this = this;

    _classCallCheck(this, RendererStore);

    _defineProperty(this, "__store", void 0);

    _defineProperty(this, "storeObserver", new _StoreObserver["default"]());

    _defineProperty(this, "setObservers", (0, _ramda.once)(function () {
      var observe = _this.storeObserver.observe;
      observe(_documentTitle["default"]);
      observe(_isLoading["default"]);
      observe(_loadingMap["default"]);
      observe(_requestedCallbacks["default"]);
      observe(_prioritizedCallbacks["default"]);
      observe(_executingCallbacks["default"]);
      observe(_executedCallbacks["default"]);
      observe(_storedCallbacks["default"]);
    }));

    _defineProperty(this, "createAppStore", function (reducer, middleware) {
      _this.__store = (0, _redux.createStore)(reducer, middleware);

      _this.storeObserver.setStore(_this.__store);

      _this.setObservers();
    });

    _defineProperty(this, "initializeStore", function (reset) {
      if (_this.__store && !reset) {
        return _this.__store;
      }

      var reducer = (0, _reducer.createReducer)(); // eslint-disable-next-line no-process-env

      if (process.env.NODE_ENV === 'production') {
        _this.createAppStore(reducer, (0, _redux.applyMiddleware)(_reduxThunk["default"]));
      } else {
        // only attach logger to middleware in non-production mode
        var reduxDTEC = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__;

        if (reduxDTEC) {
          _this.createAppStore(reducer, reduxDTEC((0, _redux.applyMiddleware)(_reduxThunk["default"])));
        } else {
          _this.createAppStore(reducer, (0, _redux.applyMiddleware)(_reduxThunk["default"]));
        }
      }

      if (!reset) {
        // TODO - Protect this under a debug mode?
        window.store = _this.__store;
      }

      if (module.hot) {
        // Enable hot module replacement for reducers
        module.hot.accept('./reducers/reducer', function () {
          var nextRootReducer = require('./reducers/reducer').createReducer();

          _this.__store.replaceReducer(nextRootReducer);
        });
      }

      return _this.__store;
    });

    this.__store = this.initializeStore();
  }

  _createClass(RendererStore, [{
    key: "store",
    get: function get() {
      return this.__store;
    }
  }]);

  return RendererStore;
}();

exports["default"] = RendererStore;