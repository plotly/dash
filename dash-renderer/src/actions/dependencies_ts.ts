import {
    flatten,
    keys,
    map,
    partition,
    pickBy,
    assoc
} from 'ramda';
import { ICallback } from '../reducers/callbacks';
import { getCallbacksByInput, splitIdAndProp } from './dependencies';
import { getPath } from './paths';

export function includeObservers(id: any, props: any, graphs: any, paths: any): ICallback[] {
    return flatten(map(
        propName => getCallbacksByInput(graphs, paths, id, propName),
        keys(props)
    ));
}

export function pruneCallbacks<T extends ICallback>(callbacks: T[], paths: any): {
    initial: T[],
    modified: T[],
    removed: T[],
    pruned: number
} {
    const [, affected] = partition(
        ({ getOutputs, callback: { outputs } }) => flatten(getOutputs(paths)).length === outputs.length,
        callbacks
    );

    const [removed, initial] = partition(
        ({ getOutputs }) => !flatten(getOutputs(paths)).length,
        affected
    );

    const modified = map(
        cb => assoc('changedPropIds', pickBy(
            (_, propId) => getPath(paths, splitIdAndProp(propId).id),
            cb.changedPropIds
        ), cb),
        initial
    );

    return {
        initial,
        modified,
        removed,
        pruned: initial.length + removed.length
    };
}