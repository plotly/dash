"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.DashRenderer = void 0;

var _react = _interopRequireDefault(require("react"));

var _reactDom = _interopRequireDefault(require("react-dom"));

var _AppProvider = _interopRequireDefault(require("./AppProvider.react"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var DashRenderer = function DashRenderer(hooks) {
  _classCallCheck(this, DashRenderer);

  // render Dash Renderer upon initialising!
  _reactDom["default"].render(_react["default"].createElement(_AppProvider["default"], {
    hooks: hooks
  }), document.getElementById('react-entry-point'));
};

exports.DashRenderer = DashRenderer;