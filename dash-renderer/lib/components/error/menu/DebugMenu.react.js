"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.DebugMenu = void 0;

var _react = _interopRequireWildcard(require("react"));

var _ramda = require("ramda");

require("./DebugMenu.css");

var _DebugIcon = _interopRequireDefault(require("../icons/DebugIcon.svg"));

var _WhiteCloseIcon = _interopRequireDefault(require("../icons/WhiteCloseIcon.svg"));

var _BellIcon = _interopRequireDefault(require("../icons/BellIcon.svg"));

var _BellIconGrey = _interopRequireDefault(require("../icons/BellIconGrey.svg"));

var _GraphIcon = _interopRequireDefault(require("../icons/GraphIcon.svg"));

var _GraphIconGrey = _interopRequireDefault(require("../icons/GraphIconGrey.svg"));

var _propTypes = _interopRequireDefault(require("prop-types"));

var _DebugAlertContainer = require("./DebugAlertContainer.react");

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

var DebugMenu = /*#__PURE__*/function (_Component) {
  _inherits(DebugMenu, _Component);

  function DebugMenu(props) {
    var _this;

    _classCallCheck(this, DebugMenu);

    _this = _possibleConstructorReturn(this, _getPrototypeOf(DebugMenu).call(this, props));
    _this.state = {
      opened: false,
      alertsOpened: false,
      callbackGraphOpened: false,
      toastsEnabled: true
    };
    return _this;
  }

  _createClass(DebugMenu, [{
    key: "render",
    value: function render() {
      var _this2 = this;

      var _this$state = this.state,
          opened = _this$state.opened,
          alertsOpened = _this$state.alertsOpened,
          toastsEnabled = _this$state.toastsEnabled,
          callbackGraphOpened = _this$state.callbackGraphOpened;
      var _this$props = this.props,
          error = _this$props.error,
          graphs = _this$props.graphs;
      var menuClasses = opened ? 'dash-debug-menu dash-debug-menu--opened' : 'dash-debug-menu dash-debug-menu--closed';
      var menuContent = opened ? _react["default"].createElement("div", {
        className: "dash-debug-menu__content"
      }, callbackGraphOpened ? _react["default"].createElement(_CallbackGraphContainer.CallbackGraphContainer, {
        graphs: graphs
      }) : null, error.frontEnd.length > 0 || error.backEnd.length > 0 ? _react["default"].createElement("div", {
        className: "dash-debug-menu__button-container"
      }, _react["default"].createElement(_DebugAlertContainer.DebugAlertContainer, {
        errors: (0, _ramda.concat)(error.frontEnd, error.backEnd),
        alertsOpened: alertsOpened,
        onClick: function onClick() {
          return _this2.setState({
            alertsOpened: !alertsOpened
          });
        }
      })) : null, _react["default"].createElement("div", {
        className: "dash-debug-menu__button-container"
      }, _react["default"].createElement("div", {
        className: "dash-debug-menu__button ".concat(callbackGraphOpened ? 'dash-debug-menu__button--enabled' : ''),
        onClick: function onClick() {
          return _this2.setState({
            callbackGraphOpened: !callbackGraphOpened
          });
        }
      }, callbackGraphOpened ? _react["default"].createElement(_GraphIcon["default"], {
        className: "dash-debug-menu__icon dash-debug-menu__icon--graph"
      }) : _react["default"].createElement(_GraphIconGrey["default"], {
        className: "dash-debug-menu__icon dash-debug-menu__icon--bell"
      })), _react["default"].createElement("label", {
        className: "dash-debug-menu__button-label"
      }, "Callback Graph")), _react["default"].createElement("div", {
        className: "dash-debug-menu__button-container"
      }, _react["default"].createElement("div", {
        className: "dash-debug-menu__button ".concat(toastsEnabled ? 'dash-debug-menu__button--enabled' : ''),
        onClick: function onClick() {
          return _this2.setState({
            toastsEnabled: !toastsEnabled
          });
        }
      }, toastsEnabled ? _react["default"].createElement(_BellIcon["default"], {
        className: "dash-debug-menu__icon dash-debug-menu__icon--bell"
      }) : _react["default"].createElement(_BellIconGrey["default"], {
        className: "dash-debug-menu__icon dash-debug-menu__icon--bell"
      })), _react["default"].createElement("label", {
        className: "dash-debug-menu__button-label"
      }, "Errors")), _react["default"].createElement("div", {
        className: "dash-debug-menu__button-container"
      }, _react["default"].createElement("div", {
        className: "dash-debug-menu__button dash-debug-menu__button--small",
        onClick: function onClick(e) {
          e.stopPropagation();

          _this2.setState({
            opened: false
          });
        }
      }, _react["default"].createElement(_WhiteCloseIcon["default"], {
        className: "dash-debug-menu__icon--close"
      })))) : _react["default"].createElement(_DebugIcon["default"], {
        className: "dash-debug-menu__icon dash-debug-menu__icon--debug"
      });
      var alertsLabel = error.frontEnd.length + error.backEnd.length > 0 && !opened ? _react["default"].createElement("div", {
        className: "dash-debug-alert-label"
      }, _react["default"].createElement("div", {
        className: "dash-debug-alert"
      }, "\uD83D\uDED1 \xA0", error.frontEnd.length + error.backEnd.length)) : null;
      return _react["default"].createElement("div", null, alertsLabel, _react["default"].createElement("div", {
        className: menuClasses,
        onClick: function onClick() {
          return _this2.setState({
            opened: true
          });
        }
      }, menuContent), _react["default"].createElement(_GlobalErrorOverlay["default"], {
        error: error,
        visible: !((0, _ramda.isEmpty)(error.backEnd) && (0, _ramda.isEmpty)(error.frontEnd)),
        toastsEnabled: toastsEnabled
      }, this.props.children));
    }
  }]);

  return DebugMenu;
}(_react.Component);

exports.DebugMenu = DebugMenu;
DebugMenu.propTypes = {
  children: _propTypes["default"].object,
  error: _propTypes["default"].object,
  graphs: _propTypes["default"].object
};