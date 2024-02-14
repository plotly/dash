import {updateProps, notifyObservers} from '../actions/index';
import {getPath} from '../actions/paths';

const setProps = (updates: {}) => {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    const ds = (window.dash_stores = window.dash_stores || []);
    for (let y = 0; y < ds.length; y++) {
        const {dispatch, getState} = ds[y];
        const {paths} = getState();
        Object.entries(updates).forEach(([componentId, props]) => {
            const componentPath = getPath(paths, componentId);
            dispatch(
                updateProps({
                    props,
                    itempath: componentPath
                })
            );
            dispatch(notifyObservers({id: componentId, props}));
        });
    }
};


const dc = (window.dash_clientside = window.dash_clientside || {});
dc['setProps'] = setProps;
