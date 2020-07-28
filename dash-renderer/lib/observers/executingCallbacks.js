"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _ramda = require("ramda");

var _callbacks = require("../actions/callbacks");

function ownKeys(object, enumerableOnly) { var keys = Object.keys(object); if (Object.getOwnPropertySymbols) { var symbols = Object.getOwnPropertySymbols(object); if (enumerableOnly) symbols = symbols.filter(function (sym) { return Object.getOwnPropertyDescriptor(object, sym).enumerable; }); keys.push.apply(keys, symbols); } return keys; }

function _objectSpread(target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i] != null ? arguments[i] : {}; if (i % 2) { ownKeys(Object(source), true).forEach(function (key) { _defineProperty(target, key, source[key]); }); } else if (Object.getOwnPropertyDescriptors) { Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)); } else { ownKeys(Object(source)).forEach(function (key) { Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key)); }); } } return target; }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function _asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

function _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _unsupportedIterableToArray(arr, i) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function _iterableToArrayLimit(arr, i) { if (typeof Symbol === "undefined" || !(Symbol.iterator in Object(arr))) return; var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

var observer = {
  observer: function observer(_ref) {
    var dispatch = _ref.dispatch,
        getState = _ref.getState;

    var _getState = getState(),
        executing = _getState.callbacks.executing;

    var _partition = (0, _ramda.partition)(function (cb) {
      return cb.executionPromise instanceof Promise;
    }, executing),
        _partition2 = _slicedToArray(_partition, 2),
        deferred = _partition2[0],
        skippedOrReady = _partition2[1];

    dispatch((0, _callbacks.aggregateCallbacks)([executing.length ? (0, _callbacks.removeExecutingCallbacks)(executing) : null, deferred.length ? (0, _callbacks.addWatchedCallbacks)(deferred) : null, skippedOrReady.length ? (0, _callbacks.addExecutedCallbacks)(skippedOrReady.map(function (cb) {
      return (0, _ramda.assoc)('executionResult', cb.executionPromise, cb);
    })) : null]));
    (0, _ramda.forEach)( /*#__PURE__*/function () {
      var _ref2 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee(cb) {
        var result, _getState2, watched, currentCb;

        return regeneratorRuntime.wrap(function _callee$(_context) {
          while (1) {
            switch (_context.prev = _context.next) {
              case 0:
                _context.next = 2;
                return cb.executionPromise;

              case 2:
                result = _context.sent;
                _getState2 = getState(), watched = _getState2.callbacks.watched; // Check if it's been removed from the `watched` list since - on callback completion, another callback may be cancelled
                // Find the callback instance or one that matches its promise (eg. could have been pruned)

                currentCb = (0, _ramda.find)(function (_cb) {
                  return _cb === cb || _cb.executionPromise === cb.executionPromise;
                }, watched);

                if (currentCb) {
                  _context.next = 7;
                  break;
                }

                return _context.abrupt("return");

              case 7:
                // Otherwise move to `executed` and remove from `watched`
                dispatch((0, _callbacks.aggregateCallbacks)([(0, _callbacks.removeWatchedCallbacks)([currentCb]), (0, _callbacks.addExecutedCallbacks)([_objectSpread(_objectSpread({}, currentCb), {}, {
                  executionResult: result
                })])]));

              case 8:
              case "end":
                return _context.stop();
            }
          }
        }, _callee);
      }));

      return function (_x) {
        return _ref2.apply(this, arguments);
      };
    }(), deferred);
  },
  inputs: ['callbacks.executing']
};
var _default = observer;
exports["default"] = _default;