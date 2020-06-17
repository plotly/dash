"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.DebugMenu = void 0;

var _react = _interopRequireWildcard(require("react"));

var _propTypes = _interopRequireDefault(require("prop-types"));

require("./DebugMenu.css");

var _BellIcon = _interopRequireDefault(require("../icons/BellIcon.svg"));

var _CheckIcon = _interopRequireDefault(require("../icons/CheckIcon.svg"));

var _ClockIcon = _interopRequireDefault(require("../icons/ClockIcon.svg"));

var _DebugIcon = _interopRequireDefault(require("../icons/DebugIcon.svg"));

var _GraphIcon = _interopRequireDefault(require("../icons/GraphIcon.svg"));

var _OffIcon = _interopRequireDefault(require("../icons/OffIcon.svg"));

var _GlobalErrorOverlay = _interopRequireDefault(require("../GlobalErrorOverlay.react"));

var _CallbackGraphContainer = require("../CallbackGraph/CallbackGraphContainer.react");

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

var classes = function classes(base, variant, variant2) {
  return "".concat(base, " ").concat(base, "--").concat(variant) + (variant2 ? " ".concat(base, "--").concat(variant2) : '');
};

var buttonFactory = function buttonFactory(enabled, buttonVariant, toggle, _Icon, iconVariant, label) {
  return _react["default"].createElement("div", {
    className: "dash-debug-menu__button-container"
  }, _react["default"].createElement("div", {
    className: classes('dash-debug-menu__button', buttonVariant, enabled && 'enabled'),
    onClick: toggle
  }, _react["default"].createElement(_Icon, {
    className: classes('dash-debug-menu__icon', iconVariant)
  }), label ? _react["default"].createElement("label", {
    className: "dash-debug-menu__button-label"
  }, label) : null));
};

var DebugMenu = /*#__PURE__*/function (_Component) {
  _inherits(DebugMenu, _Component);

  function DebugMenu(props) {
    var _this;

    _classCallCheck(this, DebugMenu);

    _this = _possibleConstructorReturn(this, _getPrototypeOf(DebugMenu).call(this, props));
    _this.state = {
      opened: false,
      callbackGraphOpened: false,
      errorsOpened: true
    };
    return _this;
  }

  _createClass(DebugMenu, [{
    key: "render",
    value: function render() {
      var _this2 = this;

      var _this$state = this.state,
          opened = _this$state.opened,
          errorsOpened = _this$state.errorsOpened,
          callbackGraphOpened = _this$state.callbackGraphOpened;
      var _this$props = this.props,
          error = _this$props.error,
          graphs = _this$props.graphs,
          hotReload = _this$props.hotReload;
      var errCount = error.frontEnd.length + error.backEnd.length;
      var connected = error.backEndConnected;

      var toggleErrors = function toggleErrors() {
        _this2.setState({
          errorsOpened: !errorsOpened
        });
      };

      var status = hotReload ? connected ? 'available' : 'unavailable' : 'cold';

      var _StatusIcon = hotReload ? connected ? _CheckIcon["default"] : _OffIcon["default"] : _ClockIcon["default"];

      var menuContent = opened ? _react["default"].createElement("div", {
        className: "dash-debug-menu__content"
      }, callbackGraphOpened ? _react["default"].createElement(_CallbackGraphContainer.CallbackGraphContainer, {
        graphs: graphs
      }) : null, buttonFactory(callbackGraphOpened, 'callbacks', function () {
        _this2.setState({
          callbackGraphOpened: !callbackGraphOpened
        });
      }, _GraphIcon["default"], 'graph', 'Callbacks'), buttonFactory(errorsOpened, 'errors', toggleErrors, _BellIcon["default"], 'bell', errCount + ' Error' + (errCount === 1 ? '' : 's')), buttonFactory(false, status, null, _StatusIcon, 'indicator', 'Server')) : _react["default"].createElement("div", {
        className: "dash-debug-menu__content"
      });
      var alertsLabel = (errCount || !connected) && !opened ? _react["default"].createElement("div", {
        className: "dash-debug-alert-label"
      }, _react["default"].createElement("div", {
        className: "dash-debug-alert",
        onClick: toggleErrors
      }, errCount ? _react["default"].createElement("div", {
        className: "dash-debug-error-count"
      }, '🛑 ' + errCount) : null, connected ? null : _react["default"].createElement("div", {
        className: "dash-debug-disconnected"
      }, "\uD83D\uDEAB"))) : null;
      var openVariant = opened ? 'open' : 'closed';
      return _react["default"].createElement("div", null, alertsLabel, _react["default"].createElement("div", {
        className: classes('dash-debug-menu__outer', openVariant)
      }, menuContent), _react["default"].createElement("div", {
        className: classes('dash-debug-menu', openVariant),
        onClick: function onClick() {
          _this2.setState({
            opened: !opened
          });
        }
      }, _react["default"].createElement(_DebugIcon["default"], {
        className: classes('dash-debug-menu__icon', 'debug')
      })), _react["default"].createElement(_GlobalErrorOverlay["default"], {
        error: error,
        visible: errCount > 0,
        errorsOpened: errorsOpened
      }, this.props.children));
    }
  }]);

  return DebugMenu;
}(_react.Component);

exports.DebugMenu = DebugMenu;
DebugMenu.propTypes = {
  children: _propTypes["default"].object,
  error: _propTypes["default"].object,
  graphs: _propTypes["default"].object,
  hotReload: _propTypes["default"].bool
};