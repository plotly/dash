"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _ramda = require("ramda");

var _callbacks = require("../actions/callbacks");

var _dependencies = require("../actions/dependencies");

var _dependencies_ts = require("../actions/dependencies_ts");

var _isAppReady = _interopRequireDefault(require("../actions/isAppReady"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

function ownKeys(object, enumerableOnly) { var keys = Object.keys(object); if (Object.getOwnPropertySymbols) { var symbols = Object.getOwnPropertySymbols(object); if (enumerableOnly) symbols = symbols.filter(function (sym) { return Object.getOwnPropertyDescriptor(object, sym).enumerable; }); keys.push.apply(keys, symbols); } return keys; }

function _objectSpread(target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i] != null ? arguments[i] : {}; if (i % 2) { ownKeys(Object(source), true).forEach(function (key) { _defineProperty(target, key, source[key]); }); } else if (Object.getOwnPropertyDescriptors) { Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)); } else { ownKeys(Object(source)).forEach(function (key) { Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key)); }); } } return target; }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

function _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _unsupportedIterableToArray(arr, i) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _iterableToArrayLimit(arr, i) { if (typeof Symbol === "undefined" || !(Symbol.iterator in Object(arr))) return; var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function _asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

function _toConsumableArray(arr) { return _arrayWithoutHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableSpread(); }

function _nonIterableSpread() { throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function _arrayWithoutHoles(arr) { if (Array.isArray(arr)) return _arrayLikeToArray(arr); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

var sortPriority = function sortPriority(c1, c2) {
  var _c1$priority, _c2$priority;

  return ((_c1$priority = c1.priority) !== null && _c1$priority !== void 0 ? _c1$priority : '') > ((_c2$priority = c2.priority) !== null && _c2$priority !== void 0 ? _c2$priority : '') ? -1 : 1;
};

var getStash = function getStash(cb, paths) {
  var getOutputs = cb.getOutputs;
  var allOutputs = getOutputs(paths);
  var flatOutputs = (0, _ramda.flatten)(allOutputs);
  var allPropIds = [];
  var reqOut = {};
  flatOutputs.forEach(function (_ref) {
    var id = _ref.id,
        property = _ref.property;
    var idStr = (0, _dependencies.stringifyId)(id);
    var idOut = reqOut[idStr] = reqOut[idStr] || [];
    idOut.push(property);
    allPropIds.push((0, _dependencies_ts.combineIdAndProp)({
      id: idStr,
      property: property
    }));
  });
  return {
    allOutputs: allOutputs,
    allPropIds: allPropIds
  };
};

var getIds = function getIds(cb, paths) {
  return (0, _ramda.uniq)((0, _ramda.pluck)('id', [].concat(_toConsumableArray((0, _ramda.flatten)(cb.getInputs(paths))), _toConsumableArray((0, _ramda.flatten)(cb.getState(paths))))));
};

var observer = {
  observer: function () {
    var _observer = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2(_ref2) {
      var dispatch, getState, _getState, _getState$callbacks, executing, watched, config, hooks, layout, paths, _getState2, prioritized, available, _partition, _partition2, syncCallbacks, asyncCallbacks, pickedSyncCallbacks, pickedAsyncCallbacks, deffered;

      return regeneratorRuntime.wrap(function _callee2$(_context2) {
        while (1) {
          switch (_context2.prev = _context2.next) {
            case 0:
              dispatch = _ref2.dispatch, getState = _ref2.getState;
              _getState = getState(), _getState$callbacks = _getState.callbacks, executing = _getState$callbacks.executing, watched = _getState$callbacks.watched, config = _getState.config, hooks = _getState.hooks, layout = _getState.layout, paths = _getState.paths;
              _getState2 = getState(), prioritized = _getState2.callbacks.prioritized;
              available = Math.max(0, 12 - executing.length - watched.length); // Order prioritized callbacks based on depth and breadth of callback chain

              prioritized = (0, _ramda.sort)(sortPriority, prioritized); // Divide between sync and async

              _partition = (0, _ramda.partition)(function (cb) {
                return (0, _isAppReady["default"])(layout, paths, getIds(cb, paths)) === true;
              }, prioritized), _partition2 = _slicedToArray(_partition, 2), syncCallbacks = _partition2[0], asyncCallbacks = _partition2[1];
              pickedSyncCallbacks = syncCallbacks.slice(0, available);
              pickedAsyncCallbacks = asyncCallbacks.slice(0, available - pickedSyncCallbacks.length);

              if (pickedSyncCallbacks.length) {
                dispatch((0, _callbacks.aggregateCallbacks)([(0, _callbacks.removePrioritizedCallbacks)(pickedSyncCallbacks), (0, _callbacks.addExecutingCallbacks)((0, _ramda.map)(function (cb) {
                  return (0, _callbacks.executeCallback)(cb, config, hooks, paths, layout, getStash(cb, paths));
                }, pickedSyncCallbacks))]));
              }

              if (pickedAsyncCallbacks.length) {
                deffered = (0, _ramda.map)(function (cb) {
                  return _objectSpread(_objectSpread(_objectSpread({}, cb), getStash(cb, paths)), {}, {
                    isReady: (0, _isAppReady["default"])(layout, paths, getIds(cb, paths))
                  });
                }, pickedAsyncCallbacks);
                dispatch((0, _callbacks.aggregateCallbacks)([(0, _callbacks.removePrioritizedCallbacks)(pickedAsyncCallbacks), (0, _callbacks.addBlockedCallbacks)(deffered)]));
                (0, _ramda.forEach)( /*#__PURE__*/function () {
                  var _ref3 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee(cb) {
                    var _getState3, blocked, currentCb, executingCallback;

                    return regeneratorRuntime.wrap(function _callee$(_context) {
                      while (1) {
                        switch (_context.prev = _context.next) {
                          case 0:
                            _context.next = 2;
                            return cb.isReady;

                          case 2:
                            _getState3 = getState(), blocked = _getState3.callbacks.blocked; // Check if it's been removed from the `blocked` list since - on callback completion, another callback may be cancelled
                            // Find the callback instance or one that matches its promise (eg. could have been pruned)

                            currentCb = (0, _ramda.find)(function (_cb) {
                              return _cb === cb || _cb.isReady === cb.isReady;
                            }, blocked);

                            if (currentCb) {
                              _context.next = 6;
                              break;
                            }

                            return _context.abrupt("return");

                          case 6:
                            executingCallback = (0, _callbacks.executeCallback)(cb, config, hooks, paths, layout, cb);
                            dispatch((0, _callbacks.aggregateCallbacks)([(0, _callbacks.removeBlockedCallbacks)([cb]), (0, _callbacks.addExecutingCallbacks)([executingCallback])]));

                          case 8:
                          case "end":
                            return _context.stop();
                        }
                      }
                    }, _callee);
                  }));

                  return function (_x2) {
                    return _ref3.apply(this, arguments);
                  };
                }(), deffered);
              }

            case 10:
            case "end":
              return _context2.stop();
          }
        }
      }, _callee2);
    }));

    function observer(_x) {
      return _observer.apply(this, arguments);
    }

    return observer;
  }(),
  inputs: ['callbacks.prioritized', 'callbacks.completed']
};
var _default = observer;
exports["default"] = _default;