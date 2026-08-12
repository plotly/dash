import {
    append,
    assocPath,
    concat,
    dissocPath,
    empty,
    equals,
    has,
    insert,
    is,
    path,
    prepend,
    reverse
} from 'ramda';

import {stringifyId} from './dependencies';
import {isDryComponent} from '../wrapper/wrapping';
import {PatchAnalysis} from './patchAnalysis';

type PatchOperation = {
    operation: string;
    location: LocationIndex[];
    params: any;
};

type LocationIndex = string | number;
type PatchHandler = (previous: any, patchUpdate: PatchOperation) => any;

export function isPatch(obj: any): boolean {
    return has('__dash_patch_update', obj);
}

function getLocationIndex(value: LocationIndex, previous: any) {
    if (is(Number, value) && value < 0) {
        return previous.length + value;
    }
    return value;
}

function getLocationPath(location: LocationIndex[], obj: any) {
    const current = [];

    for (let i = 0; i < location.length; i++) {
        const value = getLocationIndex(location[i], path(current, obj));
        current.push(value);
    }

    return current;
}

export class PatchBuilder {
    private operations: PatchOperation[] = [];

    assign(location: LocationIndex[], value: any) {
        this.operations.push({
            operation: 'Assign',
            location,
            params: {value}
        });
        return this;
    }

    merge(location: LocationIndex[], value: any) {
        this.operations.push({
            operation: 'Merge',
            location,
            params: {value}
        });
        return this;
    }

    extend(location: LocationIndex[], value: any) {
        this.operations.push({
            operation: 'Extend',
            location,
            params: {value}
        });
        return this;
    }

    delete(location: LocationIndex[]) {
        this.operations.push({
            operation: 'Delete',
            location,
            params: {}
        });
        return this;
    }

    insert(location: LocationIndex[], index: number, value: any) {
        this.operations.push({
            operation: 'Insert',
            location,
            params: {index, value}
        });
        return this;
    }

    append(location: LocationIndex[], value: any) {
        this.operations.push({
            operation: 'Append',
            location,
            params: {value}
        });
        return this;
    }

    prepend(location: LocationIndex[], value: any) {
        this.operations.push({
            operation: 'Prepend',
            location,
            params: {value}
        });
        return this;
    }

    add(location: LocationIndex[], value: any) {
        this.operations.push({
            operation: 'Add',
            location,
            params: {value}
        });
        return this;
    }

    sub(location: LocationIndex[], value: any) {
        this.operations.push({
            operation: 'Sub',
            location,
            params: {value}
        });
        return this;
    }

    mul(location: LocationIndex[], value: any) {
        this.operations.push({
            operation: 'Mul',
            location,
            params: {value}
        });
        return this;
    }

    div(location: LocationIndex[], value: any) {
        this.operations.push({
            operation: 'Div',
            location,
            params: {value}
        });
        return this;
    }

    clear(location: LocationIndex[]) {
        this.operations.push({
            operation: 'Clear',
            location,
            params: {}
        });
        return this;
    }

    reverse(location: LocationIndex[]) {
        this.operations.push({
            operation: 'Reverse',
            location,
            params: {}
        });
        return this;
    }

    remove(location: LocationIndex[], value: any) {
        this.operations.push({
            operation: 'Remove',
            location,
            params: {value}
        });
        return this;
    }

    build() {
        return {
            __dash_patch_update: '__dash_patch_update',
            operations: this.operations
        };
    }
}

const patchHandlers: {[k: string]: PatchHandler} = {
    Assign: (previous, patchOperation) => {
        const {params, location} = patchOperation;
        return assocPath(location, params.value, previous);
    },
    Merge: (previous, patchOperation) => {
        const prev: any = path(patchOperation.location, previous);
        return assocPath(
            patchOperation.location,
            {
                ...prev,
                ...patchOperation.params.value
            },
            previous
        );
    },
    Extend: (previous, patchOperation) => {
        const prev: any = path(patchOperation.location, previous);
        return assocPath(
            patchOperation.location,
            concat(prev, patchOperation.params.value),
            previous
        );
    },
    Delete: (previous, patchOperation) => {
        return dissocPath(patchOperation.location, previous);
    },
    Insert: (previous, patchOperation) => {
        const prev: any = path(patchOperation.location, previous);
        return assocPath(
            patchOperation.location,
            insert(
                getLocationIndex(patchOperation.params.index, prev),
                patchOperation.params.value,
                prev
            ),
            previous
        );
    },
    Append: (previous, patchOperation) => {
        const prev: any = path(patchOperation.location, previous);
        return assocPath(
            patchOperation.location,
            append(patchOperation.params.value, prev),
            previous
        );
    },
    Prepend: (previous, patchOperation) => {
        const prev: any = path(patchOperation.location, previous);
        return assocPath(
            patchOperation.location,
            prepend(patchOperation.params.value, prev),
            previous
        );
    },
    Add: (previous, patchOperation) => {
        const prev: any = path(patchOperation.location, previous);
        return assocPath(
            patchOperation.location,
            prev + patchOperation.params.value,
            previous
        );
    },
    Sub: (previous, patchOperation) => {
        const prev: any = path(patchOperation.location, previous);
        return assocPath(
            patchOperation.location,
            prev - patchOperation.params.value,
            previous
        );
    },
    Mul: (previous, patchOperation) => {
        const prev: any = path(patchOperation.location, previous);
        return assocPath(
            patchOperation.location,
            prev * patchOperation.params.value,
            previous
        );
    },
    Div: (previous, patchOperation) => {
        const prev: any = path(patchOperation.location, previous);
        return assocPath(
            patchOperation.location,
            prev / patchOperation.params.value,
            previous
        );
    },
    Clear: (previous, patchOperation) => {
        const prev: any = path(patchOperation.location, previous);
        return assocPath(patchOperation.location, empty(prev), previous);
    },
    Reverse: (previous, patchOperation) => {
        const prev: any = path(patchOperation.location, previous);
        return assocPath(patchOperation.location, reverse(prev), previous);
    },
    Remove: (previous, patchOperation) => {
        const prev: any = path(patchOperation.location, previous);
        return assocPath(
            patchOperation.location,
            prev.filter(
                (item: any) => !equals(item, patchOperation.params.value)
            ),
            previous
        );
    }
};

/*
 * Operations that put a value into the tree, which add/remove ids,
 * and need to be handled during a patch
 */
const insertingOperations: {[operation: string]: true} = {
    Assign: true,
    Merge: true,
    Extend: true,
    Insert: true,
    Append: true,
    Prepend: true
};

function collectComponentIds(
    value: any,
    freshIds: PatchAnalysis['freshIds'],
    visited: Set<any>
) {
    if (!value || typeof value !== 'object' || visited.has(value)) {
        return;
    }
    visited.add(value);

    if (Array.isArray(value)) {
        value.forEach(item => collectComponentIds(item, freshIds, visited));
        return;
    }

    if (isDryComponent(value)) {
        const {id} = value.props;
        if (id !== undefined && id !== null) {
            freshIds[stringifyId(id)] = true;
        }
        collectComponentIds(value.props, freshIds, visited);
        return;
    }

    for (const key in value) {
        collectComponentIds(value[key], freshIds, visited);
    }
}

function recordWrittenProp(
    previous: any,
    location: LocationIndex[],
    writtenProps: PatchAnalysis['writtenProps']
) {
    let current = previous;
    let idStr: string | null = null;
    let property: string | null = null;

    for (let i = 0; i < location.length && current; i++) {
        const key = location[i];
        if (
            key === 'props' &&
            i + 1 < location.length &&
            isDryComponent(current) &&
            current.props.id !== undefined &&
            current.props.id !== null
        ) {
            idStr = stringifyId(current.props.id);
            property = String(location[i + 1]);
        }
        current = current[key];
    }

    if (idStr !== null && property !== null) {
        const props = writtenProps[idStr] || (writtenProps[idStr] = {});
        props[property] = true;
    }
}

/*
 * Operations that only add items at the end of a list, and how many items
 * each one adds. Anything else that touches a list's top level (Insert,
 * Prepend, Delete, Remove, Clear, Reverse, Assign) invalidates the
 * append-only shortcut for that property, since old items can no longer be
 * assumed to have kept their indices.
 */
const tailAppendCounts: {[operation: string]: (params: any) => number} = {
    Append: () => 1,
    Extend: params => (Array.isArray(params.value) ? params.value.length : 0)
};

function recordTailAppend(
    property: string | undefined,
    location: LocationIndex[],
    operation: string,
    params: any,
    analysis: PatchAnalysis
) {
    if (property === undefined) {
        return;
    }
    if (analysis.tailAppends[property] === false) {
        // Already invalidated for this property; nothing can undo that.
        return;
    }
    if (location.length === 0 && operation in tailAppendCounts) {
        analysis.tailAppends[property] =
            (analysis.tailAppends[property] || 0) +
            tailAppendCounts[operation](params);
        return;
    }
    analysis.tailAppends[property] = false;
}

function recordPatchOperation(
    previous: any,
    patchOperation: PatchOperation,
    analysis: PatchAnalysis,
    property?: string
) {
    const {operation, location, params} = patchOperation;

    if (insertingOperations[operation]) {
        collectComponentIds(params.value, analysis.freshIds, new Set());
    }

    recordTailAppend(property, location, operation, params, analysis);

    if (operation === 'Merge' && params.value && is(Object, params.value)) {
        Object.keys(params.value).forEach(key =>
            recordWrittenProp(
                previous,
                location.concat(key),
                analysis.writtenProps
            )
        );
        return;
    }

    recordWrittenProp(previous, location, analysis.writtenProps);
}

export function handlePatch<T>(
    previousValue: T,
    patchValue: any,
    analysis?: PatchAnalysis,
    property?: string
): T {
    let reducedValue = previousValue;

    for (let i = 0; i < patchValue.operations.length; i++) {
        const patch = patchValue.operations[i];
        patch.location = getLocationPath(patch.location, reducedValue);
        const handler = patchHandlers[patch.operation];
        if (!handler) {
            throw new Error(`Invalid Operation ${patch.operation}`);
        }
        if (analysis) {
            recordPatchOperation(reducedValue, patch, analysis, property);
        }
        reducedValue = handler(reducedValue, patch);
    }

    return reducedValue;
}

/*
 * `analysis`, when provided, is filled in with what the patches did.
 * Props that are not patches are left out of it, so callers
 * can tell a patched prop from a fully replaced one
 */
export function parsePatchProps(
    props: any,
    previousProps: any,
    analysis?: PatchAnalysis
): Record<string, any> {
    if (!is(Object, props)) {
        return props;
    }

    const patchedProps: any = {};

    for (const key of Object.keys(props)) {
        const val = props[key];
        if (isPatch(val)) {
            const previousValue = previousProps[key];
            if (previousValue === undefined) {
                throw new Error('Cannot patch undefined');
            }
            if (analysis) {
                analysis.patchedProps[key] = true;
            }
            patchedProps[key] = handlePatch(previousValue, val, analysis, key);
        } else {
            patchedProps[key] = val;
        }
    }

    return patchedProps;
}
