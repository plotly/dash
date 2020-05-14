import {
    assoc,
    concat,
    flatten,
    keys,
    map,
    mergeWith,
    partition,
    pickBy,
    unnest
} from 'ramda';
import { ICallback, ICallbackProperty } from '../reducers/callbacks';
import { getCallbacksByInput, splitIdAndProp, stringifyId } from './dependencies';
import { getPath } from './paths';

export const DIRECT = 2;
export const INDIRECT = 1;
export const mergeMax = mergeWith(Math.max);

export const combineIdAndProp = ({
    id,
    property
}: ICallbackProperty) => `${stringifyId(id)}.${property}`;

export const getUniqueIdentifier = ({
    anyVals,
    callback: {
        inputs,
        outputs,
        state
    }
}: ICallback): string => concat(
    map(combineIdAndProp, [
        ...inputs,
        ...outputs,
        ...state,
    ]),
    Array.isArray(anyVals) ?
        anyVals :
        anyVals === '' ? [] : [anyVals]
    ).join(',');

export function includeObservers(id: any, props: any, graphs: any, paths: any): ICallback[] {
    return followForward(graphs, paths, flatten(map(
        propName => getCallbacksByInput(graphs, paths, id, propName),
        keys(props)
    )));
}

export function pruneCallbacks<T extends ICallback>(callbacks: T[], paths: any): {
    added: T[],
    removed: T[]
} {
    const [, removed] = partition(
        ({ getOutputs, callback: { outputs } }) => flatten(getOutputs(paths)).length === outputs.length,
        callbacks
    );

    const [, modified] = partition(
        ({ getOutputs }) => !flatten(getOutputs(paths)).length,
        removed
    );

    const added = map(
        cb => assoc('changedPropIds', pickBy(
            (_, propId) => getPath(paths, splitIdAndProp(propId).id),
            cb.changedPropIds
        ), cb),
        modified
    );

    return {
        added,
        removed
    };
}

/*
 * Take a list of callbacks and follow them all forward, ie see if any of their
 * outputs are inputs of another callback. Any new callbacks get added to the
 * list. All that come after another get marked as blocked by that one, whether
 * they were in the initial list or not.
 */
export function followForward(graphs: any, paths: any, callbacks: ICallback[]): ICallback[] {
    callbacks = callbacks.slice(0);
    let i;
    let callback: ICallback;

    const followOutput = ({ id, property }: ICallbackProperty) => {
        callbacks = concat(callbacks, getCallbacksByInput(
            graphs,
            paths,
            id,
            property,
            INDIRECT
        ));
    };

    // Using a for loop instead of forEach because followOutput may extend the
    // callbacks array, and we want to continue into these new elements.
    for (i = 0; i < callbacks.length; i++) {
        callback = callbacks[i];
        const outputs = unnest(callback.getOutputs(paths));
        outputs.forEach(followOutput);
    }
    return callbacks;
}
