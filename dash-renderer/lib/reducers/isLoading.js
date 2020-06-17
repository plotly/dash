"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = exports.IsLoadingActionType = void 0;
var IsLoadingActionType;
exports.IsLoadingActionType = IsLoadingActionType;

(function (IsLoadingActionType) {
  IsLoadingActionType["Set"] = "IsLoading.Set";
})(IsLoadingActionType || (exports.IsLoadingActionType = IsLoadingActionType = {}));

var DEFAULT_STATE = true;

var _default = function _default() {
  var state = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : DEFAULT_STATE;
  var action = arguments.length > 1 ? arguments[1] : undefined;
  return action.type === IsLoadingActionType.Set ? action.payload : state;
};

exports["default"] = _default;