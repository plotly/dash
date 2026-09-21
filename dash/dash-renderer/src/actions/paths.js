import {
    concat,
    filter,
    find,
    forEachObjIndexed,
    insert,
    propEq,
    props,
    indexOf
} from 'ramda';

import {crawlLayout} from './utils';

/*
 * state.paths has structure:
 * {
 *   strs: {[id]: path} // for regular string ids
 *   objs: {[keyStr]: [{values, path}]} // for wildcard ids, in layout order
 *   objIndex: {[keyStr]: {[valuesKey]: path}} // O(1) exact lookup for getPath
 * }
 * keyStr: sorted keys of the id, joined with ',' into one string
 * values: array of values in the id, in order of keys
 * valuesKey: those values serialized, so an exact id resolves to its path
 *   without a linear scan of every component that shares the id's key set
 *   (what made resolving an ALL/MATCH callback over N components O(N^2))
 *
 * `objs` stays an ordered array because pattern matching (MATCH/ALLSMALLER)
 * and `getAllPMCIds` walk it in order; `objIndex` is the fast path only for
 * exact lookups. A paths object that predates `objIndex` (an empty initial
 * state, a hand-built test fixture) simply has none, and getPath falls back
 * to the linear scan - so the two are always kept consistent by construction.
 */

const valuesKey = values => JSON.stringify(values);

export function computePaths(subTree, startingPath, oldPaths, events) {
    const {
        strs: oldStrs,
        objs: oldObjs,
        objIndex: oldObjIndex = {}
    } = oldPaths || {strs: {}, objs: {}};

    const diffHead = path => startingPath.some((v, i) => path[i] !== v);

    const spLen = startingPath.length;
    // if we're updating a subtree, clear out all of the existing items
    const strs = spLen ? filter(diffHead, oldStrs) : {};
    const objs = {};

    // objIndex mirrors objs as a valuesKey->path map for O(1) getPath. For a
    // subtree update we keep the old maps and only touch the keyStrs whose
    // entries actually change (copy-on-write), so re-resolving one small
    // chunk doesn't rebuild the index for every unrelated wildcard component.
    const objIndex = spLen ? {...oldObjIndex} : {};
    const touched = new Set();
    const editMap = keyStr => {
        if (!touched.has(keyStr)) {
            objIndex[keyStr] = {...(objIndex[keyStr] || {})};
            touched.add(keyStr);
        }
        return objIndex[keyStr];
    };

    if (spLen) {
        forEachObjIndexed((oldValPaths, oldKeys) => {
            const newVals = [];
            oldValPaths.forEach(entry => {
                if (diffHead(entry.path)) {
                    newVals.push(entry); // outside the chunk: carried over
                } else {
                    // inside the chunk being replaced: drop it, the crawl
                    // below re-adds whatever is still there
                    delete editMap(oldKeys)[valuesKey(entry.values)];
                }
            });
            if (newVals.length) {
                objs[oldKeys] = newVals;
            }
        }, oldObjs);
    }

    crawlLayout(subTree, (child, itempath) => {
        const id = child.props && child.props.id;
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
                const map = editMap(keyStr);
                const k = valuesKey(values);
                if (!(k in map)) {
                    // first match wins, matching the old `find` semantics
                    map[k] = item.path;
                }
            } else {
                strs[id] = concat(startingPath, itempath);
            }
        }
    });

    // We include an event emitter here because it will be used along with
    // paths to determine when the app is ready for callbacks.
    return {strs, objs, objIndex, events: events || oldPaths.events};
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
    // Only extend the index if the old table already had one - otherwise
    // it would be incomplete (missing the pre-existing entries) and getPath
    // must keep falling back to the linear scan on `objs`.
    const objIndex = oldPaths.objIndex ? {...oldPaths.objIndex} : null;

    newItems.forEach((child, i) => {
        crawlLayout(child, (c, itempath) => {
            const id = c.props && c.props.id;
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
        if (objIndex) {
            const map = {...(objIndex[keyStr] || {})};
            newObjItems[keyStr].forEach(({values, path: p}) => {
                const k = valuesKey(values);
                if (!(k in map)) {
                    map[k] = p;
                }
            });
            objIndex[keyStr] = map;
        }
    });

    return {
        strs,
        objs,
        ...(objIndex ? {objIndex} : {}),
        events: oldPaths.events
    };
}

export function getPath(paths, id) {
    if (typeof id === 'object') {
        const keys = Object.keys(id).sort();
        const keyStr = keys.join(',');
        const values = props(keys, id);
        // O(1) exact lookup when the table carries an index (always, once it
        // has been through computePaths/appendPaths). A present index is
        // complete, so a miss means the id genuinely isn't on the page.
        if (paths.objIndex) {
            const map = paths.objIndex[keyStr];
            return (map && map[valuesKey(values)]) || false;
        }
        const keyPaths = paths.objs[keyStr];
        if (!keyPaths) {
            return false;
        }
        const pathObj = find(propEq(values, 'values'), keyPaths);
        return pathObj && pathObj.path;
    }
    return paths.strs[id];
}
