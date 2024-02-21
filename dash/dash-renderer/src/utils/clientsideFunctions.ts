import {updateProps, notifyObservers} from '../actions/index';
import {getPath} from '../actions/paths';

const set_props = (id: string | object, props: {[k: string]: any}) => {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    const ds = (window.dash_stores = window.dash_stores || []);
    for (let y = 0; y < ds.length; y++) {
        const {dispatch, getState} = ds[y];
        const {paths} = getState();
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        const componentPath = getPath(paths, id);
        dispatch(
            updateProps({
                props,
                itempath: componentPath
            })
        );
        dispatch(notifyObservers({id, props}));
    }
};

// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
const dc = (window.dash_clientside = window.dash_clientside || {});
dc['set_props'] = set_props;
