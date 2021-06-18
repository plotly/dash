import {has, includes} from 'ramda';

export function propTypeErrorHandler(message, props, type) {
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

    const messageParts = message.split('`');
    let errorMessage;
    if (includes('is marked as required', message)) {
        const invalidPropPath = messageParts[1];
        errorMessage = `${invalidPropPath} in ${type}`;
        if (props.id) {
            errorMessage += ` with ID "${props.id}"`;
        }
        errorMessage += ' is required but it was not provided.';
    } else if (includes('Bad object', message)) {
        /*
         * Handle .exact errors
         * https://github.com/facebook/prop-types/blob/v15.7.2/factoryWithTypeCheckers.js#L438-L442
         */
        errorMessage =
            message.split('supplied to ')[0] +
            `supplied to ${type}` +
            '.\nBad' +
            message.split('.\nBad')[1];
    } else if (
        includes('Invalid ', message) &&
        includes(' supplied to ', message)
    ) {
        const invalidPropPath = messageParts[1];

        errorMessage = `Invalid argument \`${invalidPropPath}\` passed into ${type}`;
        if (props.id) {
            errorMessage += ` with ID "${props.id}"`;
        }
        errorMessage += '.';

        /*
         * Not all error messages include the expected value.
         * In particular, oneOfType.
         * https://github.com/facebook/prop-types/blob/v15.7.2/factoryWithTypeCheckers.js#L388
         */
        if (includes(', expected ', message)) {
            const expectedPropType = message.split(', expected ')[1];
            errorMessage += `\nExpected ${expectedPropType}`;
        }

        /*
         * Not all error messages include the type
         * In particular, oneOfType.
         * https://github.com/facebook/prop-types/blob/v15.7.2/factoryWithTypeCheckers.js#L388
         */
        if (includes(' of type `', message)) {
            const invalidPropTypeProvided = message
                .split(' of type `')[1]
                .split('`')[0];
            errorMessage += `\nWas supplied type \`${invalidPropTypeProvided}\`.`;
        }

        if (has(invalidPropPath, props)) {
            /*
             * invalidPropPath may be nested like `options[0].value`.
             * For now, we won't try to unpack these nested options
             * but we could in the future.
             */
            const jsonSuppliedValue = JSON.stringify(
                props[invalidPropPath],
                null,
                2
            );
            if (jsonSuppliedValue) {
                if (includes('\n', jsonSuppliedValue)) {
                    errorMessage += `\nValue provided: \n${jsonSuppliedValue}`;
                } else {
                    errorMessage += `\nValue provided: ${jsonSuppliedValue}`;
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
