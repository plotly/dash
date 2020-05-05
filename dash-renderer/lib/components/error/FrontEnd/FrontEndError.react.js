"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.FrontEndError = void 0;

var _reactRedux = require("react-redux");

require("./FrontEndError.css");

var _react = require("react");

var _CollapseIcon = _interopRequireDefault(require("../icons/CollapseIcon.svg"));

var _propTypes = _interopRequireDefault(require("prop-types"));

require("../Percy.css");

var _utils = require("../../../actions/utils");

var _werkzeugcss = _interopRequireDefault(require("../werkzeugcss"));

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

var FrontEndError = /*#__PURE__*/function (_Component) {
  _inherits(FrontEndError, _Component);

  function FrontEndError(props) {
    var _this;

    _classCallCheck(this, FrontEndError);

    _this = _possibleConstructorReturn(this, _getPrototypeOf(FrontEndError).call(this, props));
    _this.state = {
      collapsed: _this.props.isListItem
    };
    return _this;
  }

  _createClass(FrontEndError, [{
    key: "render",
    value: function render() {
      var _this2 = this;

      var _this$props = this.props,
          e = _this$props.e,
          inAlertsTray = _this$props.inAlertsTray;
      var collapsed = this.state.collapsed;
      var cardClasses = 'dash-error-card__content' + (inAlertsTray ? ' dash-error-card--alerts-tray' : '');
      /* eslint-disable no-inline-comments */

      var errorHeader = React.createElement("div", {
        className: "dash-fe-error-top test-devtools-error-toggle",
        onClick: function onClick() {
          return _this2.setState({
            collapsed: !collapsed
          });
        }
      }, React.createElement("span", {
        className: "dash-fe-error-top__group"
      }, "\u26D1\uFE0F", React.createElement("span", {
        className: "dash-fe-error__title"
      }, e.error.message || 'Error')), React.createElement("span", {
        className: "dash-fe-error-top__group"
      }, React.createElement("span", {
        className: "dash-fe-error__timestamp percy-hide"
      }, "".concat(e.timestamp.toLocaleTimeString())), React.createElement("span", {
        className: "dash-fe-error__timestamp percy-show"
      }, "00:00:00 PM"), React.createElement(_CollapseIcon["default"], {
        className: "dash-fe-error__collapse ".concat(collapsed ? 'dash-fe-error__collapse--flipped' : ''),
        onClick: function onClick() {
          return _this2.setState({
            collapsed: !collapsed
          });
        }
      })));
      /* eslint-enable no-inline-comments */

      return collapsed ? React.createElement("div", {
        className: "dash-error-card__list-item"
      }, errorHeader) : React.createElement("div", {
        className: cardClasses
      }, errorHeader, React.createElement(ErrorContent, {
        error: e.error
      }));
    }
  }]);

  return FrontEndError;
}(_react.Component);

exports.FrontEndError = FrontEndError;
var MAX_MESSAGE_LENGTH = 40;
/* eslint-disable no-inline-comments */

function UnconnectedErrorContent(_ref) {
  var error = _ref.error,
      base = _ref.base;
  return React.createElement("div", {
    className: "error-container"
  }, typeof error.message !== 'string' || error.message.length < MAX_MESSAGE_LENGTH ? null : React.createElement("div", {
    className: "dash-fe-error__st"
  }, React.createElement("div", {
    className: "dash-fe-error__info dash-fe-error__curved"
  }, error.message)), typeof error.stack !== 'string' ? null : React.createElement("div", {
    className: "dash-fe-error__st"
  }, React.createElement("div", {
    className: "dash-fe-error__info"
  }, React.createElement("details", null, React.createElement("summary", null, React.createElement("i", null, "(This error originated from the built-in JavaScript code that runs Dash apps. Click to see the full stack trace or open your browser's console.)")), error.stack.split('\n').map(function (line, i) {
    return React.createElement("p", {
      key: i
    }, line);
  })))), typeof error.html !== 'string' ? null : error.html.indexOf('<!DOCTYPE HTML') === 0 ? React.createElement("div", {
    className: "dash-be-error__st"
  }, React.createElement("div", {
    className: "dash-backend-error"
  }, React.createElement("iframe", {
    srcDoc: error.html.replace('</head>', "<style type=\"text/css\">".concat(_werkzeugcss["default"], "</style></head>")).replace('="?__debugger__', "=\"".concat(base, "?__debugger__")),
    style: {
      /*
       * 67px of padding and margin between this
       * iframe and the parent container.
       * 67 was determined manually in the
       * browser's dev tools.
       */
      width: 'calc(600px - 67px)',
      height: '75vh',
      border: 'none'
    }
  }))) : React.createElement("div", {
    className: "dash-be-error__str"
  }, React.createElement("div", {
    className: "dash-backend-error"
  }, error.html)));
}
/* eslint-enable no-inline-comments */


var errorPropTypes = _propTypes["default"].shape({
  message: _propTypes["default"].string,

  /* front-end error messages */
  stack: _propTypes["default"].string,

  /* backend error messages */
  html: _propTypes["default"].string
});

UnconnectedErrorContent.propTypes = {
  error: errorPropTypes,
  base: _propTypes["default"].string
};
var ErrorContent = (0, _reactRedux.connect)(function (state) {
  return {
    base: (0, _utils.urlBase)(state.config)
  };
})(UnconnectedErrorContent);
FrontEndError.propTypes = {
  e: _propTypes["default"].shape({
    timestamp: _propTypes["default"].object,
    error: errorPropTypes
  }),
  inAlertsTray: _propTypes["default"].bool,
  isListItem: _propTypes["default"].bool
};
FrontEndError.defaultProps = {
  inAlertsTray: false,
  isListItem: false
};