import checkPropTypes from '../checkPropTypes';
import {propTypeErrorHandler} from '../exceptions';
import {validateComponent} from './wrapping';

type CheckedComponentProps = {
    children: JSX.Element;
    element: any;
    component: any;
    props?: any;
};

export default function CheckedComponent(p: CheckedComponentProps) {
    const {element, props, children, component} = p;

    validateComponent(component);

    const errorMessage = checkPropTypes(
        element.propTypes,
        props,
        'component prop',
        element
    );
    if (errorMessage) {
        propTypeErrorHandler(errorMessage, props, component.type);
    }

    return children;
}
