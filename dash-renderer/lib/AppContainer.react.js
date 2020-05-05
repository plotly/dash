"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _reactRedux = require("react-redux");

var _react = _interopRequireDefault(require("react"));

var _propTypes = _interopRequireDefault(require("prop-types"));

var _APIController = _interopRequireDefault(require("./APIController.react"));

var _DocumentTitle = _interopRequireDefault(require("./components/core/DocumentTitle.react"));

var _Loading = _interopRequireDefault(require("./components/core/Loading.react"));

var _Toolbar = _interopRequireDefault(require("./components/core/Toolbar.react"));

var _Reloader = _interopRequireDefault(require("./components/core/Reloader.react"));

var _index = require("./actions/index");

var _ramda = require("ramda");

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

var UnconnectedAppContainer = /*#__PURE__*/function (_React$Component) {
  _inherits(UnconnectedAppContainer, _React$Component);

  function UnconnectedAppContainer(props) {
    var _this;

    _classCallCheck(this, UnconnectedAppContainer);

    _this = _possibleConstructorReturn(this, _getPrototypeOf(UnconnectedAppContainer).call(this, props));

    if (props.hooks.request_pre !== null || props.hooks.request_post !== null) {
      props.dispatch((0, _index.setHooks)(props.hooks));
    }

    return _this;
  }

  _createClass(UnconnectedAppContainer, [{
    key: "UNSAFE_componentWillMount",
    value: function UNSAFE_componentWillMount() {
      var dispatch = this.props.dispatch;
      var config = JSON.parse(document.getElementById('_dash-config').textContent); // preset common request params in the config

      config.fetch = {
        credentials: 'same-origin',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json'
        }
      };
      dispatch((0, _index.setConfig)(config));
    }
  }, {
    key: "render",
    value: function render() {
      var config = this.props.config;

      if ((0, _ramda.type)(config) === 'Null') {
        return _react["default"].createElement("div", {
          className: "_dash-loading"
        }, "Loading...");
      }

      var show_undo_redo = config.show_undo_redo;
      return _react["default"].createElement(_react["default"].Fragment, null, show_undo_redo ? _react["default"].createElement(_Toolbar["default"], null) : null, _react["default"].createElement(_APIController["default"], null), _react["default"].createElement(_DocumentTitle["default"], null), _react["default"].createElement(_Loading["default"], null), _react["default"].createElement(_Reloader["default"], null));
    }
  }]);

  return UnconnectedAppContainer;
}(_react["default"].Component);

UnconnectedAppContainer.propTypes = {
  hooks: _propTypes["default"].object,
  dispatch: _propTypes["default"].func,
  config: _propTypes["default"].object
};
var AppContainer = (0, _reactRedux.connect)(function (state) {
  return {
    history: state.history,
    config: state.config
  };
}, function (dispatch) {
  return {
    dispatch: dispatch
  };
})(UnconnectedAppContainer);
var _default = AppContainer;
exports["default"] = _default;