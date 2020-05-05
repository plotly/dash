"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _reactRedux = require("react-redux");

var _react = require("react");

var _propTypes = _interopRequireDefault(require("prop-types"));

var _radium = _interopRequireDefault(require("radium"));

var _actions = require("../../actions");

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

var UnconnectedComponentErrorBoundary = /*#__PURE__*/function (_Component) {
  _inherits(UnconnectedComponentErrorBoundary, _Component);

  function UnconnectedComponentErrorBoundary(props) {
    var _this;

    _classCallCheck(this, UnconnectedComponentErrorBoundary);

    _this = _possibleConstructorReturn(this, _getPrototypeOf(UnconnectedComponentErrorBoundary).call(this, props));
    _this.state = {
      myID: props.componentId,
      oldChildren: null,
      hasError: false
    };
    return _this;
  }

  _createClass(UnconnectedComponentErrorBoundary, [{
    key: "componentDidCatch",
    value: function componentDidCatch(error, info) {
      var dispatch = this.props.dispatch;
      dispatch((0, _actions.onError)({
        myID: this.state.myID,
        type: 'frontEnd',
        error: error,
        info: info
      }));
      dispatch(_actions.revert);
    }
  }, {
    key: "componentDidUpdate",
    value: function componentDidUpdate(prevProps, prevState) {
      var prevChildren = prevProps.children;

      if (!this.state.hasError && prevChildren !== prevState.oldChildren && prevChildren !== this.props.children) {
        /* eslint-disable-next-line react/no-did-update-set-state */
        this.setState({
          oldChildren: prevChildren
        });
      }
    }
  }, {
    key: "render",
    value: function render() {
      var _this$state = this.state,
          hasError = _this$state.hasError,
          oldChildren = _this$state.oldChildren;
      return hasError ? oldChildren : this.props.children;
    }
  }], [{
    key: "getDerivedStateFromError",
    value: function getDerivedStateFromError(_) {
      return {
        hasError: true
      };
    }
  }]);

  return UnconnectedComponentErrorBoundary;
}(_react.Component);

UnconnectedComponentErrorBoundary.propTypes = {
  children: _propTypes["default"].object,
  componentId: _propTypes["default"].string,
  error: _propTypes["default"].object,
  dispatch: _propTypes["default"].func
};
var ComponentErrorBoundary = (0, _reactRedux.connect)(function (state) {
  return {
    error: state.error
  };
}, function (dispatch) {
  return {
    dispatch: dispatch
  };
})((0, _radium["default"])(UnconnectedComponentErrorBoundary));
var _default = ComponentErrorBoundary;
exports["default"] = _default;