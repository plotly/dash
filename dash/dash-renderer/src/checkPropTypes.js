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
    componentName
) {
    return Object.keys(values)
        .reduce((acc, propName) => {
            if (typeSpecs && typeSpecs[propName] !== undefined) {
                const error = typeSpecs[propName](
                    values,
                    propName,
                    componentName,
                    location,
                    null,
                    ReactPropTypesSecret
                );
                if (error) {
                    acc.push(error);
                }
            }
            return acc;
        }, [])
        .join('\n\n');
}
