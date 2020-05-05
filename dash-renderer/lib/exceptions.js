"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.propTypeErrorHandler = propTypeErrorHandler;

var _ramda = require("ramda");

function propTypeErrorHandler(message, props, type) {
  /*
   * propType error messages are constructed in
   * https://github.com/facebook/prop-types/blob/v15.7.2/factoryWithTypeCheckers.js
   * (Version 15.7.2)
   *
   * Parse these exception objects to remove JS source code and improve
   * the clarity.
   *
   * If wrong prop type was passed in, message looks like:
   *
   * Error: "Failed component prop type: Invalid component prop `animate` of type `number` supplied to `function GraphWithDefaults(props) {
   *   var id = props.id ? props.id : generateId();
   *   return react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement(PlotlyGraph, _extends({}, props, {
   *     id: id
   *   }));
   * }`, expected `boolean`."
   *
   *
   * If a required prop type was omitted, message looks like:
   *
   * "Failed component prop type: The component prop `options[0].value` is marked as required in `function Checklist(props) {
   *    var _this;
   *
   *    _classCallCheck(this, Checklist);
   *
   *     _this = _possibleConstructorReturn(this, _getPrototypeOf(Checklist).call(this, props));
   *     _this.state = {
   *       values: props.values
   *     };
   *     return _this;
   *   }`, but its value is `undefined`."
   *
   */
  var messageParts = message.split('`');
  var errorMessage;

  if ((0, _ramda.includes)('is marked as required', message)) {
    var invalidPropPath = messageParts[1];
    errorMessage = "".concat(invalidPropPath, " in ").concat(type);

    if (props.id) {
      errorMessage += " with ID \"".concat(props.id, "\"");
    }

    errorMessage += " is required but it was not provided.";
  } else if ((0, _ramda.includes)('Bad object', message)) {
    /*
     * Handle .exact errors
     * https://github.com/facebook/prop-types/blob/v15.7.2/factoryWithTypeCheckers.js#L438-L442
     */
    errorMessage = message.split('supplied to ')[0] + "supplied to ".concat(type) + '.\nBad' + message.split('.\nBad')[1];
  } else if ((0, _ramda.includes)('Invalid ', message) && (0, _ramda.includes)(' supplied to ', message)) {
    var _invalidPropPath = messageParts[1];
    errorMessage = "Invalid argument `".concat(_invalidPropPath, "` passed into ").concat(type);

    if (props.id) {
      errorMessage += " with ID \"".concat(props.id, "\"");
    }

    errorMessage += '.';
    /*
     * Not all error messages include the expected value.
     * In particular, oneOfType.
     * https://github.com/facebook/prop-types/blob/v15.7.2/factoryWithTypeCheckers.js#L388
     */

    if ((0, _ramda.includes)(', expected ', message)) {
      var expectedPropType = message.split(', expected ')[1];
      errorMessage += "\nExpected ".concat(expectedPropType);
    }
    /*
     * Not all error messages include the type
     * In particular, oneOfType.
     * https://github.com/facebook/prop-types/blob/v15.7.2/factoryWithTypeCheckers.js#L388
     */


    if ((0, _ramda.includes)(' of type `', message)) {
      var invalidPropTypeProvided = message.split(' of type `')[1].split('`')[0];
      errorMessage += "\nWas supplied type `".concat(invalidPropTypeProvided, "`.");
    }

    if ((0, _ramda.has)(_invalidPropPath, props)) {
      /*
       * invalidPropPath may be nested like `options[0].value`.
       * For now, we won't try to unpack these nested options
       * but we could in the future.
       */
      var jsonSuppliedValue = JSON.stringify(props[_invalidPropPath], null, 2);

      if (jsonSuppliedValue) {
        if ((0, _ramda.includes)('\n', jsonSuppliedValue)) {
          errorMessage += "\nValue provided: \n".concat(jsonSuppliedValue);
        } else {
          errorMessage += "\nValue provided: ".concat(jsonSuppliedValue);
        }
      }
    }
  } else {
    /*
     * Not aware of other prop type warning messages.
     * But, if they exist, then at least throw the default
     * react prop types error
     */
    throw new Error(message);
  }

  throw new Error(errorMessage);
}