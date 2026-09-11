import React, {useState, useEffect} from 'react';
import {path} from 'ramda';
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
    temp?: boolean; // If true, the component will be removed on unmount.
};

/**
 * For rendering components that are out of the regular layout tree.
 */
function ExternalWrapper({component, componentPath, temp = false}: Props) {
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
            if (temp) {
                dispatch(removeComponent({componentPath}));
            }
        };
    }, []);

    useEffect(() => {
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        dispatch((_dispatch: any, getState: any) => {
            // The host subtree may have been replaced (eg. a callback
            // returned new children) while this wrapper reconciled in place
            // rather than remounting. In that case the component is gone from
            // the layout at `componentPath`, so re-insert it instead of
            // updating a path that no longer exists.
            const exists = path(componentPath, getState().layout);
            batch(() => {
                if (exists) {
                    _dispatch(
                        updateProps({
                            itempath: componentPath,
                            props: component.props
                        })
                    );
                } else {
                    _dispatch(addComponentToLayout({component, componentPath}));
                }
                if (component.props.id) {
                    _dispatch(
                        notifyObservers({
                            id: component.props.id,
                            props: component.props
                        })
                    );
                }
            });
        });
    }, [component.props]);

    if (!inserted) {
        return null;
    }
    // Render a wrapper with the actual props.
    return <DashWrapper componentPath={componentPath} />;
}
export default ExternalWrapper;
