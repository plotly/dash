import {
    all,
    any,
    assoc,
    concat,
    difference,
    filter,
    flatten,
    forEach,
    isEmpty,
    keys,
    map,
    mergeWith,
    partition,
    pickBy,
    reduce
} from 'ramda';
import { ICallback, ICallbackProperty } from '../types/callbacks';
import { getCallbacksByInput, splitIdAndProp, stringifyId, getCallbacksInLayout, isMultiValued } from './dependencies';
import { getPath } from './paths';

export const DIRECT = 2;
export const INDIRECT = 1;
export const mergeMax = mergeWith(Math.max);

export const combineIdAndProp = ({
    id,
    property
}: ICallbackProperty) => `${stringifyId(id)}.${property}`;

export const getReadyCallbacks = (
    candidates: ICallback[],
    callbacks: ICallback[] = candidates
): ICallback[] => {
    // Find all outputs of all active callbacks
    const outputs = map(
        combineIdAndProp,
        reduce<ICallback, any[]>((o, cb) => concat(o, cb.callback.outputs), [], callbacks)
    );

    // Make `outputs` hash table for faster access
    const outputsMap: { [key: string]: boolean } = {};
    forEach(output => outputsMap[output] = true, outputs);

    // Find `requested` callbacks that do not depend on a outstanding output (as either input or state)
    return filter(
        cb => all(
            cbp => !outputsMap[combineIdAndProp(cbp)],
            cb.callback.inputs
        ),
        candidates
    );
}

export const getLayoutCallbacks = (
    graphs: any,
    paths: any,
    layout: any,
    options: any
): ICallback[] => {
    let exclusions: string[] = [];
    const initial = getCallbacksInLayout(
        graphs,
        paths,
        layout,
        options
    );
    let callbacks = initial;

    while (true) {
        // Find callbacks for which all inputs are missing or in the exclusions
        const [included, excluded] = partition(({
            callback: { inputs },
            getInputs
        }) => any(isMultiValued, inputs) ||
            !isEmpty(difference(
                map(combineIdAndProp, flatten(getInputs(paths))),
                exclusions
            )),
            callbacks
        );

        // If there's no additional exclusions, break loop - callbacks have been cleaned
        if (!excluded.length) {
            break;
        }

        callbacks = included;

        // update exclusions with all additional excluded outputs
        exclusions = concat(
            exclusions,
            map(combineIdAndProp, flatten(map(
                ({ getOutputs }) => getOutputs(paths),
                excluded
            )))
        );
    }

    // only return ready callbacks (the executed callbacks will ensure followups are triggered)
    return getReadyCallbacks(callbacks);

}

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