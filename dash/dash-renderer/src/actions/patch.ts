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
