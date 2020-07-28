"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _reactRedux = require("react-redux");

var _react = _interopRequireDefault(require("react"));

var _propTypes = _interopRequireDefault(require("prop-types"));

var _ramda = require("ramda");

var _index = require("../../actions/index.js");

var _radium = _interopRequireDefault(require("radium"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

function UnconnectedToolbar(props) {
  var dispatch = props.dispatch,
      history = props.history;
  var styles = {
    parentSpanStyle: {
      display: 'inline-block',
      opacity: '0.2',
      ':hover': {
        opacity: 1
      }
    },
    iconStyle: {
      fontSize: 20
    },
    labelStyle: {
      fontSize: 15
    }
  };

  var undoLink = /*#__PURE__*/_react["default"].createElement("span", {
    key: "undoLink",
    style: (0, _ramda.mergeRight)({
      color: history.past.length ? '#0074D9' : 'grey',
      cursor: history.past.length ? 'pointer' : 'default'
    }, styles.parentSpanStyle),
    onClick: function onClick() {
      return dispatch(_index.undo);
    }
  }, /*#__PURE__*/_react["default"].createElement("div", {
    style: (0, _ramda.mergeRight)({
      transform: 'rotate(270deg)'
    }, styles.iconStyle)
  }, "\u21BA"), /*#__PURE__*/_react["default"].createElement("div", {
    style: styles.labelStyle
  }, "undo"));

  var redoLink = /*#__PURE__*/_react["default"].createElement("span", {
    key: "redoLink",
    style: (0, _ramda.mergeRight)({
      color: history.future.length ? '#0074D9' : 'grey',
      cursor: history.future.length ? 'pointer' : 'default',
      marginLeft: 10
    }, styles.parentSpanStyle),
    onClick: function onClick() {
      return dispatch(_index.redo);
    }
  }, /*#__PURE__*/_react["default"].createElement("div", {
    style: (0, _ramda.mergeRight)({
      transform: 'rotate(90deg)'
    }, styles.iconStyle)
  }, "\u21BB"), /*#__PURE__*/_react["default"].createElement("div", {
    style: styles.labelStyle
  }, "redo"));

  return /*#__PURE__*/_react["default"].createElement("div", {
    className: "_dash-undo-redo",
    style: {
      position: 'fixed',
      bottom: '30px',
      left: '30px',
      fontSize: '20px',
      textAlign: 'center',
      zIndex: '9999',
      backgroundColor: 'rgba(255, 255, 255, 0.9)'
    }
  }, /*#__PURE__*/_react["default"].createElement("div", {
    style: {
      position: 'relative'
    }
  }, history.past.length > 0 ? undoLink : null, history.future.length > 0 ? redoLink : null));
}

UnconnectedToolbar.propTypes = {
  history: _propTypes["default"].object,
  dispatch: _propTypes["default"].func
};
var Toolbar = (0, _reactRedux.connect)(function (state) {
  return {
    history: state.history
  };
}, function (dispatch) {
  return {
    dispatch: dispatch
  };
})((0, _radium["default"])(UnconnectedToolbar));
var _default = Toolbar;
exports["default"] = _default;