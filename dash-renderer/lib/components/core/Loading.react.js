"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _reactRedux = require("react-redux");

var _react = _interopRequireDefault(require("react"));

var _propTypes = _interopRequireDefault(require("prop-types"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

function Loading(props) {
  if (props.pendingCallbacks.length) {
    return _react["default"].createElement("div", {
      className: "_dash-loading-callback"
    });
  }

  return null;
}

Loading.propTypes = {
  pendingCallbacks: _propTypes["default"].array.isRequired
};

var _default = (0, _reactRedux.connect)(function (state) {
  return {
    pendingCallbacks: state.pendingCallbacks
  };
})(Loading);

exports["default"] = _default;