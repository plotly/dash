/*
 * Copied out of prop-types and modified - inspired by check-prop-types, but
 * simplified and tweaked to our needs: we don't need the NODE_ENV check,
 * we report all errors, not just the first one, and we don't need the throwing
 * variant `assertPropTypes`.
 */
import ReactPropTypesSecret from 'prop-types/lib/ReactPropTypesSecret';

/**
 * Assert that the values match with the type specs.
 *
 * @param {object} typeSpecs Map of name to a ReactPropType
 * @param {object} values Runtime values that need to be type-checked
 * @param {string} location e.g. "prop", "context", "child context"
 * @param {string} componentName Name of the component for error messages.
 * @param {?Function} getStack Returns the component stack.
 * @return {string} Any error message resulting from checking the types
 */
export default function checkPropTypes(
    typeSpecs,
    values,
    location,
    componentName,
    getStack = null
) {
    const errors = [];
    for (const typeSpecName in typeSpecs) {
        if (typeSpecs.hasOwnProperty(typeSpecName)) {
            let error;
            // Prop type validation may throw. In case they do, we don't want to
            // fail the render phase where it didn't fail before. So we log it.
            // After these have been cleaned up, we'll let them throw.
            try {
                // This is intentionally an invariant that gets caught. It's the same
                // behavior as without this statement except with a better message.
                if (typeof typeSpecs[typeSpecName] !== 'function') {
                    error = Error(
                        (componentName || 'React class') +
                            ': ' +
                            location +
                            ' type `' +
                            typeSpecName +
                            '` is invalid; ' +
                            'it must be a function, usually from the `prop-types` package, but received `' +
                            typeof typeSpecs[typeSpecName] +
                            '`.'
                    );
                    error.name = 'Invariant Violation';
                } else {
                    error = typeSpecs[typeSpecName](
                        values,
                        typeSpecName,
                        componentName,
                        location,
                        null,
                        ReactPropTypesSecret
                    );
                }
            } catch (ex) {
                error = ex;
            }
            if (error && !(error instanceof Error)) {
                errors.push(
                    (componentName || 'React class') +
                        ': type specification of ' +
                        location +
                        ' `' +
                        typeSpecName +
                        '` is invalid; the type checker ' +
                        'function must return `null` or an `Error` but returned a ' +
                        typeof error +
                        '. ' +
                        'You may have forgotten to pass an argument to the type checker ' +
                        'creator (arrayOf, instanceOf, objectOf, oneOf, oneOfType, and ' +
                        'shape all require an argument).'
                );
            }
            if (error instanceof Error) {
                var stack = (getStack && getStack()) || '';

                errors.push(
                    'Failed ' + location + ' type: ' + error.message + stack
                );
            }
        }
    }
    return errors.join('\n\n');
}
