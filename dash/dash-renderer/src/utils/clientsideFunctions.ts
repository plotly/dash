import {updateProps, notifyObservers} from '../actions/index';
import {getPath} from '../actions/paths';
import {getStores} from './stores';

/**
 * Set the props of a dash component by id or path.
 *
 * @param idOrPath Path or id of the dash component to update.
 * @param props The props to update.
 */
function set_props(
    idOrPath: string | object | string[],
    props: {[k: string]: any}
) {
    const ds = getStores();
    for (let y = 0; y < ds.length; y++) {
        const {dispatch, getState} = ds[y];
        let componentPath;
        const {paths} = getState();
        if (!Array.isArray(idOrPath)) {
            componentPath = getPath(paths, idOrPath);
        } else {
            componentPath = idOrPath;
        }
        dispatch(
            updateProps({
                props,
                itempath: componentPath,
                renderType: 'clientsideApi'
            })
        );
        dispatch(notifyObservers({id: idOrPath, props}));
    }
}

// Clean url code adapted from https://github.com/braintree/sanitize-url/blob/main/src/constants.ts
// to allow for data protocol.
const invalidProtocols = /^([^\w]*)(javascript|vbscript)/im;
const newLines = /&(tab|newline);/gi;

// eslint-disable-next-line no-control-regex
const ctrlChars = /[\u0000-\u001F\u007F-\u009F\u2000-\u200D\uFEFF]/gim;
const htmlEntities = /&#(\w+)(^\w|;)?/g;

const clean_url = (url: string, fallback = 'about:blank') => {
    if (url === '') {
        return url;
    }
    const cleaned = url
        .replace(newLines, '')
        .replace(ctrlChars, '')
        .replace(htmlEntities, (_, dec) => String.fromCharCode(dec))
        .trim();
    if (invalidProtocols.test(cleaned)) {
        return fallback;
    }
    return url;
};

const dc = ((window as any).dash_clientside =
    (window as any).dash_clientside || {});
dc['set_props'] = set_props;
dc['clean_url'] = dc['clean_url'] === undefined ? clean_url : dc['clean_url'];
