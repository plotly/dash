import {path} from 'ramda';
import {DashContext, useDashContext} from './wrapper/DashContext';
import {getPath} from './actions/paths';
import {getStores} from './utils/stores';

/**
 * Get the dash props from a component path or id.
 *
 * @param componentPathOrId The path or the id of the component to get the props of.
 * @param propPath Additional key to get the property instead of plain props.
 * @returns
 */
function getLayout(componentPathOrId: string[] | string): any {
    const ds = getStores();
    for (let y = 0; y < ds.length; y++) {
        const {paths, layout} = ds[y].getState();
        let componentPath;
        if (!Array.isArray(componentPathOrId)) {
            componentPath = getPath(paths, componentPathOrId);
        } else {
            componentPath = componentPathOrId;
        }
        const props = path(componentPath, layout);
        if (props !== undefined) {
            return props;
        }
    }
}

(window as any).dash_component_api = {
    DashContext,
    useDashContext,
    getLayout
};
