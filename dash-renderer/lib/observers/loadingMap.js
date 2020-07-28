"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _ramda = require("ramda");

var _loadingMap = require("../actions/loadingMap");

function _toConsumableArray(arr) { return _arrayWithoutHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableSpread(); }

function _nonIterableSpread() { throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function _arrayWithoutHoles(arr) { if (Array.isArray(arr)) return _arrayLikeToArray(arr); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

var observer = {
  observer: function observer(_ref) {
    var dispatch = _ref.dispatch,
        getState = _ref.getState;

    var _getState = getState(),
        _getState$callbacks = _getState.callbacks,
        executing = _getState$callbacks.executing,
        watched = _getState$callbacks.watched,
        executed = _getState$callbacks.executed,
        loadingMap = _getState.loadingMap,
        paths = _getState.paths;
    /*
        Get the path of all components impacted by callbacks
        with states: executing, watched, executed.
         For each path, keep track of all (id,prop) tuples that
        are impacted for this node and nested nodes.
    */


    var loadingPaths = (0, _ramda.flatten)((0, _ramda.map)(function (cb) {
      return cb.getOutputs(paths);
    }, [].concat(_toConsumableArray(executing), _toConsumableArray(watched), _toConsumableArray(executed))));
    var nextMap = (0, _ramda.isEmpty)(loadingPaths) ? null : (0, _ramda.reduce)(function (res, _ref2) {
      var id = _ref2.id,
          property = _ref2.property,
          path = _ref2.path;
      var target = res;
      var idprop = {
        id: id,
        property: property
      }; // Assign all affected props for this path and nested paths

      target.__dashprivate__idprops__ = target.__dashprivate__idprops__ || [];

      target.__dashprivate__idprops__.push(idprop);

      path.forEach(function (p, i) {
        var _target$p;

        target = target[p] = (_target$p = target[p]) !== null && _target$p !== void 0 ? _target$p : p === 'children' && typeof path[i + 1] === 'number' ? [] : {};
        target.__dashprivate__idprops__ = target.__dashprivate__idprops__ || [];

        target.__dashprivate__idprops__.push(idprop);
      }); // Assign one affected prop for this path

      target.__dashprivate__idprop__ = target.__dashprivate__idprop__ || idprop;
      return res;
    }, {}, loadingPaths);

    if (!(0, _ramda.equals)(nextMap, loadingMap)) {
      dispatch((0, _loadingMap.setLoadingMap)(nextMap));
    }
  },
  inputs: ['callbacks.executing', 'callbacks.watched', 'callbacks.executed']
};
var _default = observer;
exports["default"] = _default;