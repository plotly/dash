/**
 * Generalized persistence for component props
 *
 * When users input new prop values, they can be stored and reapplied later,
 * when the component is recreated (changing `Tab` for example) or when the
 * page is reloaded (depending on `persistence_type`) Storage is tied to
 * component ID and will not on with components without an ID.
 *
 * Renderer handles the mechanics, but components must define a few props:
 *
 * - `persistence`: boolean, string, or number. For simple usage, set to `true`
 *   to enable persistence, omit or set `false` to disable. For more complex
 *   scenarios, use any truthy value, and change to a *different* truthy value
 *   when you want the persisted values cleared. (modeled off `uirevision` in)
 *   plotly.js
 *   Typically should have no default, but the other persistence props should
 *   have defaults, so all a user needs to do to enable persistence is set this
 *   one prop.
 *
 * - `persisted_props`: array of prop names or "nested prop IDs" allowed to
 *   persist. Normally should default to the full list of supported props,
 *   so they can all be enabled at once. The main exception to this is if
 *   there's a prop that *can* be persisted but most users wouldn't want this.
 *   A nested prop ID describes *part* of a prop to store. It must be
 *   "<propName>.<piece>" where propName is the prop that has this info, and
 *   piece may or may not map to the exact substructure being stored but is
 *   meaningful to the user. For example, in `dash_table`, `columns.name`
 *   stores `columns[i].name` for all columns `i`. Nested props also need
 *   entries in `persistenceTransforms` - see below.
 *
 * - `persistence_type`: one of "local", "session", or "memory", just like
 *   `dcc.Store`. But the default here should be "local" because the main use
 *   case is to maintain settings across reloads.
 *
 * If any `persisted_props` are nested prop IDs, the component should define a
 * class property (not a React prop) `persistenceTransforms`, as an object:
 * {
 *   [propName]: {
 *     [piece]: {
 *       extract: propValue => valueToStore,
 *       apply: (storedValue, propValue) => newPropValue
 *     }
 *   }
 * }
 * - `extract` turns a prop value into a reduced value to store.
 * - `apply` puts an extracted value back into the prop. Make sure this creates
 *   a new object rather than mutating `proValue`, and that if there are
 *   multiple `piece` entries for one `propName`, their `apply` functions
 *   commute - which should not be an issue if they extract and apply
 *   non-intersecting parts of the full prop.
 * You only need to define these for the props that need them.
 * It's important that `extract` pulls out *only* the relevant pieces of the
 * prop, because persistence is only maintained if the extracted value of the
 * prop before applying persistence is the same as it was before the user's
 * changes.
 */

import {
    equals,
    filter,
    forEach,
    keys,
    lensPath,
    set,
    symmetricDifference,
    type,
} from 'ramda';
import {createAction} from 'redux-actions';
import uniqid from 'uniqid';

import Registry from './registry';

export const storePrefix = '_dash_persistence.';

function err(e) {
    const error = typeof e === 'string' ? new Error(e) : e;

    /* eslint-disable no-console */
    // Send this to the console too, so it's still available with debug off
    console.error(e);
    /* eslint-disable no-console */

    return createAction('ON_ERROR')({
        myUID: uniqid(),
        myID: storePrefix,
        type: 'frontEnd',
        error,
    });
}

/*
 * Does a key fit this prefix? Must either be an exact match
 * or, if a separator is provided, a scoped match - exact prefix
 * followed by the separator (then anything else)
 */
function keyPrefixMatch(prefix, separator) {
    const fullStr = prefix + separator;
    const fullLen = fullStr.length;
    return key => key === prefix || key.substr(0, fullLen) === fullStr;
}

const UNDEFINED = 'U';
const _parse = val => val === UNDEFINED ? void 0 : JSON.parse(val || null);
const _stringify = val => val === void 0 ? UNDEFINED : JSON.stringify(val);

class WebStore {
    constructor(backEnd) {
        this._name = backEnd;
        this._storage = window[backEnd];
    }

    hasItem(key) {
        return this._storage.getItem(storePrefix + key) !== null;
    }

    getItem(key) {
        // note: _storage.getItem returns null on missing keys
        // and JSON.parse(null) returns null as well
        return _parse(this._storage.getItem(storePrefix + key));
    }

    /*
     * In addition to the regular key->value to set, setItem takes
     * dispatch as a parameter, so it can report OOM to devtools
     */
    setItem(key, value, dispatch) {
        try {
            this._storage.setItem(storePrefix + key, _stringify(value));
        } catch (e) {
            if (dispatch) {
                dispatch(err(e));
            } else {
                throw e;
            }
            // TODO: Should we clear storage here? Or fall back to memory?
            // Probably not, unless we want to handle this at a higher level
            // so we can keep all 3 items in sync
        }
    }

    removeItem(key) {
        this._storage.removeItem(storePrefix + key);
    }

    /*
     * clear matching keys matching (optionally followed by a dot and more
     * characters) - or all keys associated with this store if no prefix.
     */
    clear(keyPrefix) {
        const fullPrefix = storePrefix + (keyPrefix || '');
        const keyMatch = keyPrefixMatch(fullPrefix, keyPrefix ? '.' : '');
        const keysToRemove = [];
        // 2-step process, so we don't depend on any particular behavior of
        // key order while removing some
        for (let i = 0; i < this._storage.length; i++) {
            const fullKey = this._storage.key(i);
            if (keyMatch(fullKey)) {
                keysToRemove.push(fullKey);
            }
        }
        forEach(k => this._storage.removeItem(k), keysToRemove);
    }
}

class MemStore {
    constructor() {
        this._data = {};
    }

    hasItem(key) {
        return key in this._data;
    }

    getItem(key) {
        // run this storage through JSON too so we know we get a fresh object
        // each retrieval
        return _parse(this._data[key]);
    }

    setItem(key, value) {
        this._data[key] = _stringify(value);
    }

    removeItem(key) {
        delete this._data[key];
    }

    clear(keyPrefix) {
        if (keyPrefix) {
            forEach(
                key => delete this._data[key],
                filter(keyPrefixMatch(keyPrefix, '.'), keys(this._data))
            );
        } else {
            this._data = {};
        }
    }
}

// Make a string 2^16 characters long (*2 bytes/char = 130kB), to test storage.
// That should be plenty for common persistence use cases,
// without getting anywhere near typical browser limits
const pow = 16;
function longString() {
    let s = 'Spam';
    for (let i = 2; i < pow; i++) {
        s += s;
    }
    return s;
}

export const stores = {
    memory: new MemStore(),
    // Defer testing & making local/session stores until requested.
    // That way if we have errors here they can show up in devtools.
};

const backEnds = {
    local: 'localStorage',
    session: 'sessionStorage',
};

function tryGetWebStore(backEnd, dispatch) {
    const store = new WebStore(backEnd);
    const fallbackStore = stores.memory;
    const storeTest = longString();
    const testKey = storePrefix + 'x.x';
    try {
        store.setItem(testKey, storeTest);
        if (store.getItem(testKey) !== storeTest) {
            dispatch(
                err(`${backEnd} init failed set/get, falling back to memory`)
            );
            return fallbackStore;
        }
        store.removeItem(testKey);
        return store;
    } catch (e) {
        dispatch(
            err(`${backEnd} init first try failed; clearing and retrying`)
        );
    }
    try {
        store.clear();
        store.setItem(testKey, storeTest);
        if (store.getItem(testKey) !== storeTest) {
            throw new Error('nope');
        }
        store.removeItem(testKey);
        dispatch(err(`${backEnd} init set/get succeeded after clearing!`));
        return store;
    } catch (e) {
        dispatch(err(`${backEnd} init still failed, falling back to memory`));
        return fallbackStore;
    }
}

function getStore(type, dispatch) {
    if (!stores[type]) {
        stores[type] = tryGetWebStore(backEnds[type], dispatch);
    }
    return stores[type];
}

const noopTransform = {
    extract: propValue => propValue,
    apply: (storedValue, _propValue) => storedValue,
};

const getTransform = (element, propName, propPart) =>
    propPart
        ? element.persistenceTransforms[propName][propPart]
        : noopTransform;

const getNewValKey = (id, persistedProp) => id + '.' + persistedProp;
const getOriginalValKey = newValKey => newValKey + '.orig';
const getPersistIdKey = newValKey => newValKey + '.id';

const getProps = layout => {
    const {props} = layout;
    const {id, persistence} = props;
    if (!id || !persistence) {
        // This component doesn't have persistence. To make downstream
        // tests more efficient don't return either one, so we just have to
        // test for truthy persistence.
        // But we still need to return props for consumers that look for
        // nested components
        return {props};
    }

    const element = Registry.resolve(layout);
    const persisted_props =
        props.persisted_props || element.defaultProps.persisted_props;
    const persistence_type =
        props.persistence_type || element.defaultProps.persistence_type;
    if (!persisted_props || !persistence_type) {
        return {props};
    }
    return {id, props, element, persistence, persisted_props, persistence_type};
};

export function recordUiEdit(layout, newProps, dispatch) {
    const {
        id,
        props,
        element,
        persistence,
        persisted_props,
        persistence_type,
    } = getProps(layout);
    if (!persistence) {
        return;
    }

    forEach(persistedProp => {
        const [propName, propPart] = persistedProp.split('.');
        if (newProps[propName]) {
            const storage = getStore(persistence_type, dispatch);
            const {extract} = getTransform(element, propName, propPart);

            const newValKey = getNewValKey(id, persistedProp);
            const persistIdKey = getPersistIdKey(newValKey);
            const previousVal = extract(props[propName]);
            const newVal = extract(newProps[propName]);

            // mainly for nested props with multiple persisted parts, it's
            // possible to have the same value as before - should not store
            // in this case.
            if (previousVal !== newVal) {
                if (
                    !storage.hasItem(newValKey) ||
                    storage.getItem(persistIdKey) !== persistence
                ) {
                    storage.setItem(
                        getOriginalValKey(newValKey),
                        previousVal,
                        dispatch
                    );
                    storage.setItem(persistIdKey, persistence, dispatch);
                }
                storage.setItem(newValKey, newVal, dispatch);
            }
        }
    }, persisted_props);
}

function clearUIEdit(id, persistence_type, persistedProp, dispatch) {
    const storage = getStore(persistence_type, dispatch);
    const newValKey = getNewValKey(id, persistedProp);

    if (storage.hasItem(newValKey)) {
        storage.removeItem(newValKey);
        storage.removeItem(getOriginalValKey(newValKey));
        storage.removeItem(getPersistIdKey(newValKey));
    }
}

/*
 * Used for entire layouts (on load) or partial layouts (from children
 * callbacks) to apply previously-stored UI edits to components
 */
export function applyPersistence(layout, dispatch) {
    if (type(layout) !== 'Object' || !layout.props) {
        return layout;
    }

    return persistenceMods(layout, layout, [], dispatch);
}

function persistenceMods(layout, component, path, dispatch) {
    const {
        id,
        props,
        element,
        persistence,
        persisted_props,
        persistence_type,
    } = getProps(component);

    let layoutOut = layout;
    if (persistence) {
        const storage = getStore(persistence_type, dispatch);
        const update = {};
        forEach(persistedProp => {
            const [propName, propPart] = persistedProp.split('.');
            const newValKey = getNewValKey(id, persistedProp);
            const storedPersistID = storage.getItem(getPersistIdKey(newValKey));
            const transform = getTransform(element, propName, propPart);

            if (storedPersistID) {
                if (
                    storedPersistID === persistence &&
                    equals(
                        storage.getItem(getOriginalValKey(newValKey)),
                        transform.extract(props[propName])
                    )
                ) {
                    // To handle multiple nested props, apply each stored value
                    // in turn; then at the end we'll push these into the layout
                    update[propName] = transform.apply(
                        storage.getItem(newValKey),
                        propName in update ? update[propName] : props[propName]
                    );
                } else {
                    clearUIEdit(id, persistence_type, persistedProp, dispatch);
                }
            }
        }, persisted_props);

        for (const propName in update) {
            layoutOut = set(
                lensPath(path.concat('props', propName)),
                update[propName],
                layoutOut
            );
        }
    }

    // recurse inward
    const {children} = props;
    if (Array.isArray(children)) {
        children.forEach((child, i) => {
            if (type(child) === 'Object' && child.props) {
                layoutOut = persistenceMods(
                    layoutOut,
                    child,
                    path.concat('props', 'children', i),
                    dispatch
                );
            }
        });
    } else if (type(children) === 'Object' && children.props) {
        layoutOut = persistenceMods(
            layoutOut,
            children,
            path.concat('props', 'children'),
            dispatch
        );
    }
    return layoutOut;
}

/*
 * When we receive new explicit props from a callback,
 * these override UI-driven edits of those exact props
 * but not for props nested inside children
 */
export function prunePersistence(layout, newProps, dispatch) {
    const {
        id,
        persistence,
        persisted_props,
        persistence_type,
        element,
    } = getProps(layout);
    if (!persistence) {
        return;
    }

    // first look for conditions that clear the persistence store entirely
    if (
        ('persistence' in newProps && newProps.persistence !== persistence) ||
        ('persistence_type' in newProps &&
            newProps.persistence_type !== persistence_type)
    ) {
        getStore(persistence_type, dispatch).clear(id);
        return;
    }

    // if the persisted props list itself changed, clear any props not
    // present in both the new and old
    if ('persisted_props' in newProps) {
        forEach(
            persistedProp =>
                clearUIEdit(id, persistence_type, persistedProp, dispatch),
            symmetricDifference(persisted_props, newProps.persisted_props)
        );
    }

    // now the main point - clear any edit associated with a prop that changed
    // note that this is independent of the new prop value.
    const transforms = element.persistenceTransforms || {};
    for (const propName in newProps) {
        const propTransforms = transforms[propName];
        if (propTransforms) {
            for (const propPart in propTransforms) {
                clearUIEdit(
                    id,
                    persistence_type,
                    `${propName}.${propPart}`,
                    dispatch
                );
            }
        } else {
            clearUIEdit(id, persistence_type, propName, dispatch);
        }
    }
}
