import {updateProps, notifyObservers} from '../actions/index';
import {getPath} from '../actions/paths';

const set_props = (id: string | object, props: {[k: string]: any}) => {
    const ds = ((window as any).dash_stores =
        (window as any).dash_stores || []);
    for (let y = 0; y < ds.length; y++) {
        const {dispatch, getState} = ds[y];
        const {paths} = getState();
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

const dc = ((window as any).dash_clientside =
    (window as any).dash_clientside || {});
dc['set_props'] = set_props;
