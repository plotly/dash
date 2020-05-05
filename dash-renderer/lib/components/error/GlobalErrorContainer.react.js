"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _reactRedux = require("react-redux");

var _react = _interopRequireWildcard(require("react"));

var _propTypes = _interopRequireDefault(require("prop-types"));

var _radium = _interopRequireDefault(require("radium"));

var _DebugMenu = require("./menu/DebugMenu.react");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

function _getRequireWildcardCache() { if (typeof WeakMap !== "function") return null; var cache = new WeakMap(); _getRequireWildcardCache = function _getRequireWildcardCache() { return cache; }; return cache; }

function _interopRequireWildcard(obj) { if (obj && obj.__esModule) { return obj; } if (obj === null || _typeof(obj) !== "object" && typeof obj !== "function") { return { "default": obj }; } var cache = _getRequireWildcardCache(); if (cache && cache.has(obj)) { return cache.get(obj); } var newObj = {}; var hasPropertyDescriptor = Object.defineProperty && Object.getOwnPropertyDescriptor; for (var key in obj) { if (Object.prototype.hasOwnProperty.call(obj, key)) { var desc = hasPropertyDescriptor ? Object.getOwnPropertyDescriptor(obj, key) : null; if (desc && (desc.get || desc.set)) { Object.defineProperty(newObj, key, desc); } else { newObj[key] = obj[key]; } } } newObj["default"] = obj; if (cache) { cache.set(obj, newObj); } return newObj; }

function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

function _possibleConstructorReturn(self, call) { if (call && (_typeof(call) === "object" || typeof call === "function")) { return call; } return _assertThisInitialized(self); }

function _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) _setPrototypeOf(subClass, superClass); }

function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }

var UnconnectedGlobalErrorContainer = /*#__PURE__*/function (_Component) {
  _inherits(UnconnectedGlobalErrorContainer, _Component);

  function UnconnectedGlobalErrorContainer(props) {
    _classCallCheck(this, UnconnectedGlobalErrorContainer);

    return _possibleConstructorReturn(this, _getPrototypeOf(UnconnectedGlobalErrorContainer).call(this, props));
  }

  _createClass(UnconnectedGlobalErrorContainer, [{
    key: "render",
    value: function render() {
      var _this$props = this.props,
          error = _this$props.error,
          graphs = _this$props.graphs,
          children = _this$props.children;
      return _react["default"].createElement("div", {
        id: "_dash-global-error-container"
      }, _react["default"].createElement(_DebugMenu.DebugMenu, {
        error: error,
        graphs: graphs
      }, _react["default"].createElement("div", {
        id: "_dash-app-content"
      }, children)));
    }
  }]);

  return UnconnectedGlobalErrorContainer;
}(_react.Component);

UnconnectedGlobalErrorContainer.propTypes = {
  children: _propTypes["default"].object,
  error: _propTypes["default"].object,
  graphs: _propTypes["default"].object
};
var GlobalErrorContainer = (0, _reactRedux.connect)(function (state) {
  return {
    error: state.error,
    graphs: state.graphs
  };
})((0, _radium["default"])(UnconnectedGlobalErrorContainer));
var _default = GlobalErrorContainer;
exports["default"] = _default;