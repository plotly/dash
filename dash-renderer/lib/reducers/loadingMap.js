"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = exports.LoadingMapActionType = void 0;
var LoadingMapActionType;
exports.LoadingMapActionType = LoadingMapActionType;

(function (LoadingMapActionType) {
  LoadingMapActionType["Set"] = "LoadingMap.Set";
})(LoadingMapActionType || (exports.LoadingMapActionType = LoadingMapActionType = {}));

var DEFAULT_STATE = {};

var _default = function _default() {
  var state = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : DEFAULT_STATE;
  var action = arguments.length > 1 ? arguments[1] : undefined;
  return action.type === LoadingMapActionType.Set ? action.payload : state;
};

exports["default"] = _default;