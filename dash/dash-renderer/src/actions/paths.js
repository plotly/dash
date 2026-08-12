import {
    concat,
    filter,
    find,
    forEachObjIndexed,
    insert,
    path,
    propEq,
    props,
    indexOf
} from 'ramda';

import {crawlLayout} from './utils';

/*
 * state.paths has structure:
 * {
 *   strs: {[id]: path} // for regular string ids
 *   objs: {[keyStr]: [{values, path}]} // for wildcard ids
 * }
 * keyStr: sorted keys of the id, joined with ',' into one string
 * values: array of values in the id, in order of keys
 */

export function computePaths(subTree, startingPath, oldPaths, events) {
    const {strs: oldStrs, objs: oldObjs} = oldPaths || {strs: {}, objs: {}};

    const diffHead = path => startingPath.some((v, i) => path[i] !== v);

    const spLen = startingPath.length;
    // if we're updating a subtree, clear out all of the existing items
    const strs = spLen ? filter(diffHead, oldStrs) : {};
    const objs = {};
    if (spLen) {
        forEachObjIndexed((oldValPaths, oldKeys) => {
            const newVals = filter(({path}) => diffHead(path), oldValPaths);
            if (newVals.length) {
                objs[oldKeys] = newVals;
            }
        }, oldObjs);
    }

    crawlLayout(subTree, (child, itempath) => {
        const id = path(['props', 'id'], child);
        if (id) {
            if (typeof id === 'object') {
                const keys = Object.keys(id).sort();
                const values = props(keys, id);
                const keyStr = keys.join(',');
                const paths = (objs[keyStr] = objs[keyStr] || []);
                const oldie = oldObjs[keyStr] || [];
                const item = {values, path: concat(startingPath, itempath)};
                const index = indexOf(item, oldie);
                if (index === -1) {
                    paths.push(item);
                } else {
                    objs[keyStr] = insert(index, item, paths);
                }
            } else {
                strs[id] = concat(startingPath, itempath);
            }
        }
    });

    // We include an event emitter here because it will be used along with
    // paths to determine when the app is ready for callbacks.
    return {strs, objs, events: events || oldPaths.events};
}

/*
 * Fast path for a Patch that only appended items to the tail of a children
 * list: instead of re-crawling every pre-existing child to rebuild the whole
 * id->path table (O(total children)), compute paths only for `newItems`
 * (the tail slice the patch added) and layer them onto the existing table.
 * The pre-existing entries are valid as-is because an append-only patch
 * never changes the position or identity of the items that were already
 * there (see `tailAppends` in patchAnalysis.ts, which guarantees this before
 * this function is used).
 */
export function appendPaths(newItems, startingPath, appendOffset, oldPaths) {
    const strs = {...oldPaths.strs};
    const objs = {...oldPaths.objs};
    const newObjItems = {};

    newItems.forEach((child, i) => {
        crawlLayout(child, (c, itempath) => {
            const id = path(['props', 'id'], c);
            if (!id) {
                return;
            }
            const fullPath = concat(startingPath, [appendOffset + i]).concat(
                itempath
            );
            if (typeof id === 'object') {
                const keys = Object.keys(id).sort();
                const values = props(keys, id);
                const keyStr = keys.join(',');
                (newObjItems[keyStr] = newObjItems[keyStr] || []).push({
                    values,
                    path: fullPath
                });
            } else {
                strs[id] = fullPath;
            }
        });
    });

    Object.keys(newObjItems).forEach(keyStr => {
        objs[keyStr] = concat(objs[keyStr] || [], newObjItems[keyStr]);
    });

    return {strs, objs, events: oldPaths.events};
}

export function getPath(paths, id) {
    if (typeof id === 'object') {
        const keys = Object.keys(id).sort();
        const keyStr = keys.join(',');
        const keyPaths = paths.objs[keyStr];
        if (!keyPaths) {
            return false;
        }
        const values = props(keys, id);
        const pathObj = find(propEq(values, 'values'), keyPaths);
        return pathObj && pathObj.path;
    }
    return paths.strs[id];
}
