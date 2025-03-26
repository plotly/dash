import {useEffect, useState, memo} from 'react';
import checkPropTypes from '../checkPropTypes';
import {propTypeErrorHandler} from '../exceptions';
import {validateComponent} from './wrapping';

type CheckedComponentProps = {
    children: JSX.Element;
    element: any;
    component: any;
    props?: any;
};

function CheckedComponent(p: CheckedComponentProps) {
    const {element, props, children, component} = p;
    const [error, setError] = useState('');

    useEffect(() => {
        validateComponent(component);
        const errorMessage = checkPropTypes(
            element.propTypes,
            props,
            'component prop',
            element
        );
        if (errorMessage) {
            setError(errorMessage);
        }
    }, [component, props]);

    if (error) {
        propTypeErrorHandler(error, props, component.type);
    }

    return children;
}

export default memo(CheckedComponent);
