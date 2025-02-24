import React, {useState, useEffect} from 'react';
import {batch, useDispatch} from 'react-redux';

import {DashLayoutPath} from '../types/component';
import DashWrapper from './DashWrapper';
import {
    addComponentToLayout,
    notifyObservers,
    removeComponent,
    updateProps
} from '../actions';

type Props = {
    componentPath: DashLayoutPath;
    componentType: string;
    componentNamespace: string;
    [k: string]: any;
};

/**
 * For rendering components that are out of the regular layout tree.
 */
function ExternalWrapper({
    componentType,
    componentNamespace,
    componentPath,
    ...props
}: Props) {
    const dispatch: any = useDispatch();
    const [inserted, setInserted] = useState(false);

    useEffect(() => {
        // Give empty props for the inserted components.
        // The props will come from the parent so they can be updated.
        dispatch(
            addComponentToLayout({
                component: {
                    type: componentType,
                    namespace: componentNamespace,
                    props: props
                },
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
            dispatch(updateProps({itempath: componentPath, props}));
            if (props.id) {
                dispatch(notifyObservers({id: props.id, props}));
            }
        });
    }, [props]);

    if (!inserted) {
        return null;
    }
    // Render a wrapper with the actual props.
    return <DashWrapper componentPath={componentPath} />;
}
export default ExternalWrapper;
