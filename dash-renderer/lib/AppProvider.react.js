"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _react = _interopRequireDefault(require("react"));

var _reactRedux = require("react-redux");

var _store = _interopRequireDefault(require("./store"));

var _AppContainer = _interopRequireDefault(require("./AppContainer.react"));

var _propTypes = _interopRequireDefault(require("prop-types"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

var store = (0, _store["default"])();

var AppProvider = function AppProvider(_ref) {
  var hooks = _ref.hooks;
  return _react["default"].createElement(_reactRedux.Provider, {
    store: store
  }, _react["default"].createElement(_AppContainer["default"], {
    hooks: hooks
  }));
};

AppProvider.propTypes = {
  hooks: _propTypes["default"].shape({
    request_pre: _propTypes["default"].func,
    request_post: _propTypes["default"].func
  })
};
AppProvider.defaultProps = {
  hooks: {
    request_pre: null,
    request_post: null
  }
};
var _default = AppProvider;
exports["default"] = _default;