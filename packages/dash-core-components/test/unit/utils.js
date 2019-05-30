import checkPropTypes from 'check-prop-types';

export function validate(component, props) {
    const errorMessage = checkPropTypes(
        component.propTypes,
        props,
        'prop',
        component.name
    );

    if (errorMessage) {
        throw new Error(errorMessage);
    }
}
