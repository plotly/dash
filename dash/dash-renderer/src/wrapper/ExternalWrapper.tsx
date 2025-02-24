import React, {useState, useEffect} from 'react';
import {batch, useDispatch} from 'react-redux';

import {DashComponent, DashLayoutPath} from '../types/component';
import DashWrapper from './DashWrapper';
import {
    addComponentToLayout,
    notifyObservers,
    removeComponent,
    updateProps
} from '../actions';

type Props = {
    component: DashComponent;
    componentPath: DashLayoutPath;
};

/**
 * For rendering components that are out of the regular layout tree.
 */
function ExternalWrapper({component, componentPath}: Props) {
    const dispatch: any = useDispatch();
    const [inserted, setInserted] = useState(false);

    useEffect(() => {
        // Give empty props for the inserted components.
        // The props will come from the parent so they can be updated.
        dispatch(
            addComponentToLayout({
                component,
                componentPath
            })
        );
        setInserted(true);
        return () => {
            dispatch(removeComponent({componentPath}));
        };
    }, []);

    useEffect(() => {
        batch(() => {
            dispatch(
                updateProps({itempath: componentPath, props: component.props})
            );
            if (component.props.id) {
                dispatch(
                    notifyObservers({
                        id: component.props.id,
                        props: component.props
                    })
                );
            }
        });
    }, [component.props]);

    if (!inserted) {
        return null;
    }
    // Render a wrapper with the actual props.
    return <DashWrapper componentPath={componentPath} />;
}
export default ExternalWrapper;
