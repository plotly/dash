import checkPropTypes from './checkPropTypes';
import {propTypeErrorHandler} from './exceptions';
import {createLibraryElement} from './libraries/createLibraryElement';
import PropTypes from 'prop-types';

export function CheckedComponent(p) {
    const {element, extraProps, props, children, type} = p;

    const errorMessage = checkPropTypes(
        element.propTypes,
        props,
        'component prop',
        element
    );
    if (errorMessage) {
        propTypeErrorHandler(errorMessage, props, type);
    }

    return createLibraryElement(element, props, extraProps, children);
}

CheckedComponent.propTypes = {
    children: PropTypes.any,
    element: PropTypes.any,
    layout: PropTypes.any,
    props: PropTypes.any,
    extraProps: PropTypes.any,
    id: PropTypes.string,
    type: PropTypes.string
};
