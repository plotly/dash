"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.DebugAlertContainer = void 0;

require("./DebugAlertContainer.css");

var _react = require("react");

var _propTypes = _interopRequireDefault(require("prop-types"));

var _ErrorIconWhite = _interopRequireDefault(require("../icons/ErrorIconWhite.svg"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

function _possibleConstructorReturn(self, call) { if (call && (_typeof(call) === "object" || typeof call === "function")) { return call; } return _assertThisInitialized(self); }

function _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) _setPrototypeOf(subClass, superClass); }

function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }

var DebugAlertContainer = /*#__PURE__*/function (_Component) {
  _inherits(DebugAlertContainer, _Component);

  function DebugAlertContainer(props) {
    _classCallCheck(this, DebugAlertContainer);

    return _possibleConstructorReturn(this, _getPrototypeOf(DebugAlertContainer).call(this, props));
  }

  _createClass(DebugAlertContainer, [{
    key: "render",
    value: function render() {
      var alertsOpened = this.props.alertsOpened;
      return React.createElement("div", {
        className: "dash-debug-alert-container".concat(alertsOpened ? ' dash-debug-alert-container--opened' : ''),
        onClick: this.props.onClick
      }, React.createElement("div", {
        className: "dash-debug-alert"
      }, alertsOpened ? React.createElement(_ErrorIconWhite["default"], {
        className: "dash-debug-alert-container__icon"
      }) : '🛑 ', this.props.errors.length));
    }
  }]);

  return DebugAlertContainer;
}(_react.Component);

exports.DebugAlertContainer = DebugAlertContainer;
DebugAlertContainer.propTypes = {
  errors: _propTypes["default"].object,
  alertsOpened: _propTypes["default"].bool,
  onClick: _propTypes["default"].func
};