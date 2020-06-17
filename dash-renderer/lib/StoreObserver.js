"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _ramda = require("ramda");

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

var StoreObserver = function StoreObserver(_store) {
  var _this = this;

  _classCallCheck(this, StoreObserver);

  _defineProperty(this, "_store", void 0);

  _defineProperty(this, "_unsubscribe", void 0);

  _defineProperty(this, "_observers", []);

  _defineProperty(this, "observe", function (observer, inputs) {
    if (typeof observer === 'function') {
      if (!Array.isArray(inputs)) {
        throw new Error('inputs must be an array');
      }

      _this.add(observer, inputs);

      return function () {
        return _this.remove(observer);
      };
    } else {
      _this.add(observer.observer, observer.inputs);

      return function () {
        return _this.remove(observer.observer);
      };
    }
  });

  _defineProperty(this, "setStore", function (store) {
    _this.__finalize__();

    _this.__init__(store);
  });

  _defineProperty(this, "__finalize__", function () {
    var _this$_unsubscribe;

    return (_this$_unsubscribe = _this._unsubscribe) === null || _this$_unsubscribe === void 0 ? void 0 : _this$_unsubscribe.call(_this);
  });

  _defineProperty(this, "__init__", function (store) {
    _this._store = store;

    if (store) {
      _this._unsubscribe = store.subscribe(_this.notify);
    }

    (0, _ramda.forEach)(function (o) {
      return o.lastState = null;
    }, _this._observers);
  });

  _defineProperty(this, "add", function (observer, inputs) {
    return _this._observers.push({
      inputPaths: (0, _ramda.map)(function (p) {
        return p.split('.');
      }, inputs),
      lastState: null,
      observer: observer,
      triggered: false
    });
  });

  _defineProperty(this, "notify", function () {
    var store = _this._store;

    if (!store) {
      return;
    }

    var state = store.getState();
    var triggered = (0, _ramda.filter)(function (o) {
      return !o.triggered && (0, _ramda.any)(function (i) {
        return (0, _ramda.path)(i, state) !== (0, _ramda.path)(i, o.lastState);
      }, o.inputPaths);
    }, _this._observers);
    (0, _ramda.forEach)(function (o) {
      return o.triggered = true;
    }, triggered);
    (0, _ramda.forEach)(function (o) {
      o.lastState = store.getState();
      o.observer(store);
      o.triggered = false;
    }, triggered);
  });

  _defineProperty(this, "remove", function (observer) {
    return _this._observers.splice(_this._observers.findIndex(function (o) {
      return observer === o.observer;
    }, _this._observers), 1);
  });

  this.__init__(_store);
};

exports["default"] = StoreObserver;