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
  if (props.isLoading) {
    return /*#__PURE__*/_react["default"].createElement("div", {
      className: "_dash-loading-callback"
    });
  }

  return null;
}

Loading.propTypes = {
  isLoading: _propTypes["default"].bool.isRequired
};

var _default = (0, _reactRedux.connect)(function (state) {
  return {
    isLoading: state.isLoading
  };
})(Loading);

exports["default"] = _default;