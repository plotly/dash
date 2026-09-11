/**
 * State preservation across dev-mode hot reloads.
 *
 * When `dev_tools_hot_reload_preserve_state` is enabled, UI-driven prop
 * edits (dispatched through `updateProps` with renderType 'internal') are
 * recorded in memory as [newVal, originalVal] pairs per `id.prop`. Right
 * before the Reloader triggers a reload - a soft `RELOAD` dispatch or a
 * full page reload - the record is written to sessionStorage. When the
 * fresh layout arrives, each recorded value is re-applied only if the
 * incoming initial value still equals `originalVal`: if the reloaded code
 * changed a prop's initial value, the new code wins.
 *
 * Unlike `persistence` this is dev-only, applies to all components with an
 * id regardless of their persistence props, and each saved edit is applied
 * at most once. Entries that don't match anything in the initial layout
 * stay pending so they can be applied to layout chunks inserted by initial
 * callbacks (e.g. `pages` content). A manual browser refresh never
 * restores state: the snapshot is only written when a hot reload fires,
 * and is deleted from sessionStorage as soon as it's read back.
 */

import {equals, isEmpty, lensPath, set} from 'ramda';

import {crawlLayout} from './actions/utils';
import {stringifyId} from './actions/dependencies';

// Scope the snapshot by the page's end_id, not just its path. When
// `preserve_state` is on the server persists a per-app end_id (stable across
// the reload, unique to the app - see dash/_hot_reload.py), so a different app
// served on the same URL gets a different key and can never restore this app's
// preserved state into itself.
const storeKey = endId =>
    `_dash_reload_state.${window.location.pathname}.${endId || ''}`;

// Values are stored stringified so `undefined` (prop not present) survives
// the sessionStorage round-trip distinctly from `null`.
const UNDEFINED = 'U';
const _stringify = val => (val === undefined ? UNDEFINED : JSON.stringify(val));
const _parse = val => (val === UNDEFINED ? undefined : JSON.parse(val || null));

// UI edits made since (re)hydration: {idStr: {propName: [newVal, originalVal]}}
// holding live values.
let uiEdits = {};
// Edits recovered from the snapshot, awaiting a matching component:
// {idStr: {propName: [stringifiedNewVal, stringifiedOriginalVal]}}.
// Entries are removed as they are applied or invalidated.
let pending = null;

// Test hook: forget all recorded and pending edits, as if the js context
// was freshly created.
export function resetReloadState() {
    uiEdits = {};
    pending = null;
}

// UI edits and clientside `set_props` calls are state worth preserving;
// regular callback outputs are recomputed by the initial callbacks
// re-firing after the reload. Server-side `set_props` payloads arrive as
// renderType 'callback'/'websocket' but flag themselves with
// `recordState` (transient `running`/`progress` updates don't).
const RECORDED_RENDER_TYPES = ['internal', 'clientsideApi'];

export function shouldRecordReloadEdit(component, {renderType, recordState}) {
    if (recordState || RECORDED_RENDER_TYPES.includes(renderType)) {
        return true;
    }
    // Memory-type dcc.Store data lives only in the layout, so unlike
    // local/session stores it would be lost on reload - record writes to
    // it no matter where they come from.
    return Boolean(
        component &&
            component.type === 'Store' &&
            component.namespace === 'dash_core_components' &&
            (component.props.storage_type || 'memory') === 'memory'
    );
}

export function recordReloadEdit(component, newProps) {
    const id = component && component.props && component.props.id;
    if (id === undefined || id === null) {
        return;
    }
    const idStr = stringifyId(id);
    const edits = (uiEdits[idStr] = uiEdits[idStr] || {});
    for (const propName in newProps) {
        // Keep the original value from the first edit - that's the value
        // the component started with after (re)hydration.
        const originalVal =
            propName in edits ? edits[propName][1] : component.props[propName];
        edits[propName] = [newProps[propName], originalVal];
    }
}

/*
 * Move all recorded edits to the pending store, in memory (all a soft
 * reload needs, since the js context survives) and in sessionStorage (for
 * hard reloads, where it doesn't). Called by the Reloader just before it
 * triggers a reload.
 */
export function snapshotReloadState(endId) {
    // Entries not yet re-applied since the last reload stay pending, so
    // state isn't lost when reloads happen in quick succession.
    pending = pending || {};
    for (const idStr in uiEdits) {
        const edits = uiEdits[idStr];
        const pendingEdits = (pending[idStr] = pending[idStr] || {});
        for (const propName in edits) {
            const [newVal, originalVal] = edits[propName];
            try {
                pendingEdits[propName] = [
                    _stringify(newVal),
                    _stringify(originalVal)
                ];
            } catch (e) {
                // Unserializable value - drop this prop, keep the rest.
                delete pendingEdits[propName];
            }
        }
    }
    uiEdits = {};
    try {
        window.sessionStorage.setItem(storeKey(endId), JSON.stringify(pending));
    } catch (e) {
        // Quota exceeded or sessionStorage unavailable - a hard reload
        // will lose state, but don't block the reload over it.
        /* eslint-disable-next-line no-console */
        console.warn('dash: failed to save state for hot reload.', e);
    }
}

/*
 * Merge pending recorded edits into an incoming layout (or sub-layout
 * inserted by a callback). Returns the possibly-modified layout.
 */
export function applyReloadState(layout, endId) {
    if (pending === null) {
        // Fresh js context: recover the snapshot a hard reload left in
        // sessionStorage, if any.
        pending = {};
        try {
            const stored = window.sessionStorage.getItem(storeKey(endId));
            if (stored) {
                pending = JSON.parse(stored) || {};
            }
        } catch (e) {
            // Unreadable snapshot - start fresh.
        }
    }
    // Always consume the stored snapshot so a manual browser refresh
    // (which never writes one) starts from a clean slate.
    try {
        window.sessionStorage.removeItem(storeKey(endId));
    } catch (e) {
        // sessionStorage unavailable - nothing to consume.
    }
    if (isEmpty(pending)) {
        return layout;
    }
    let layoutOut = layout;
    crawlLayout(layout, (component, componentPath) => {
        const id = component && component.props && component.props.id;
        if (id === undefined || id === null) {
            return;
        }
        const idStr = stringifyId(id);
        const edits = pending[idStr];
        if (!edits) {
            return;
        }
        for (const propName in edits) {
            let newVal, originalVal;
            try {
                newVal = _parse(edits[propName][0]);
                originalVal = _parse(edits[propName][1]);
            } catch (e) {
                delete edits[propName];
                continue;
            }
            if (equals(component.props[propName], originalVal)) {
                layoutOut = set(
                    lensPath(componentPath.concat(['props', propName])),
                    newVal,
                    layoutOut
                );
                // Re-record so the edit survives the next reload too.
                recordReloadEdit(component, {[propName]: newVal});
            }
            // Either way this entry is settled: it was applied, or the
            // initial value changed in the new code and the new code wins.
            delete edits[propName];
        }
        if (isEmpty(edits)) {
            delete pending[idStr];
        }
    });
    return layoutOut;
}
