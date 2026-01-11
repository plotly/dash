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

export function handlePatch<T>(previousValue: T, patchValue: any): T {
    let reducedValue = previousValue;

    for (let i = 0; i < patchValue.operations.length; i++) {
        const patch = patchValue.operations[i];
        patch.location = getLocationPath(patch.location, reducedValue);
        const handler = patchHandlers[patch.operation];
        if (!handler) {
            throw new Error(`Invalid Operation ${patch.operation}`);
        }
        reducedValue = handler(reducedValue, patch);
    }

    return reducedValue;
}

export function parsePatchProps(
    props: any,
    previousProps: any
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
            patchedProps[key] = handlePatch(previousValue, val);
        } else {
            patchedProps[key] = val;
        }
    }

    return patchedProps;
}
