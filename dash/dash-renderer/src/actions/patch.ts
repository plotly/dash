import {
    append,
    assocPath,
    concat,
    dissocPath,
    has,
    insert,
    path,
    prepend
} from 'ramda';

type PatchOperation = {
    operation: string;
    location: LocationIndex[];
    params: any;
};

type LocationIndex = string | number;
type PatchHandler = (previous: any, patchUpdate: PatchOperation) => any;

function isPatch(obj: any): boolean {
    return has('__dash_patch_update', obj);
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
        return insert(
            patchOperation.params.index,
            patchOperation.params.data,
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
    }
};

export function handlePatch<T>(previousValue: T, patchValue: any): T {
    if (!isPatch(patchValue)) {
        return patchValue;
    }
    let reducedValue = previousValue;

    for (let i = 0; i < patchValue.operations.length; i++) {
        const patch = patchValue.operations[i];
        const handler = patchHandlers[patch.operation];
        if (!handler) {
            throw new Error(`Invalid Operation ${patch.operation}`);
        }
        reducedValue = handler(reducedValue, patch);
    }

    return reducedValue;
}
