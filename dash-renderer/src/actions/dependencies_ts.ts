import {
    assoc,
    concat,
    flatten,
    keys,
    map,
    mergeWith,
    partition,
    pickBy
} from 'ramda';
import { ICallback, ICallbackProperty } from '../types/callbacks';
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
    return flatten(map(
        propName => getCallbacksByInput(graphs, paths, id, propName),
        keys(props)
    ));
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