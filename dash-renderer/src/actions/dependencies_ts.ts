import {
    all,
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
    props,
    reduce
} from 'ramda';
import { ICallback, ICallbackProperty } from '../types/callbacks';
import { addAllResolvedFromOutputs, splitIdAndProp, stringifyId, getCallbacksInLayout, isMultiValued, resolveDeps, idMatch } from './dependencies';
import { getPath } from './paths';

export const DIRECT = 2;
export const INDIRECT = 1;
export const mergeMax = mergeWith(Math.max);

export const combineIdAndProp = ({
    id,
    property
}: ICallbackProperty) => `${stringifyId(id)}.${property}`;

export function getCallbacksByInput(
    graphs: any,
    paths: any,
    id: any,
    prop: any,
    changeType?: any
): ICallback[] {
    const matches: ICallback[] = [];
    const idAndProp = combineIdAndProp({ id, property: prop });

    if (typeof id === 'string') {
        // standard id version
        const callbacks = (graphs.inputMap[id] || {})[prop];
        if (!callbacks) {
            return [];
        }

        callbacks.forEach(
            addAllResolvedFromOutputs(resolveDeps(), paths, matches)
        );
    } else {
        // wildcard version
        const keys = Object.keys(id).sort();
        const vals = props(keys, id);
        const keyStr = keys.join(',');
        const patterns: any[] = (graphs.inputPatterns[keyStr] || {})[prop];
        if (!patterns) {
            return [];
        }
        patterns.forEach(pattern => {
            if (idMatch(keys, vals, pattern.values)) {
                pattern.callbacks.forEach(
                    addAllResolvedFromOutputs(
                        resolveDeps(keys, vals, pattern.values),
                        paths,
                        matches
                    )
                );
            }
        });
    }
    matches.forEach(match => {
        match.changedPropIds[idAndProp] = changeType || DIRECT;
        match.priority = getPriority(graphs, paths, match)
    });
    return matches;
}

/*
 * Take a list of callbacks and follow them all forward, ie see if any of their
 * outputs are inputs of another callback. Any new callbacks get added to the
 * list. All that come after another get marked as blocked by that one, whether
 * they were in the initial list or not.
 */
export function getPriority(graphs: any, paths: any, callback: ICallback) {
    let callbacks: ICallback[] = [callback];
    let priority: number[] = [];

    while (callbacks.length) {
        const outputs = flatten(map(
            cb => flatten(cb.getOutputs(paths)),
            callbacks
        ));

        callbacks = flatten(map(
            ({ id, property }: any) => getCallbacksByInput(
                graphs,
                paths,
                id,
                property,
                INDIRECT
            ),
            outputs
        ));

        if (callbacks.length) {
            priority.push(callbacks.length);
        }
    }

    return priority;
}

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
    let callbacks = getCallbacksInLayout(
        graphs,
        paths,
        layout,
        options
    );

    /*
        Remove from the initial callbacks those that are left with only excluded inputs.

        Exclusion of inputs happens when:
        - an input is missing
        - an input in the initial callback chain depends only on excluded inputs

        Further execlusion might happen after callbacks return with:
        - PreventUpdate
        - no_update
    */
    while (true) {
        // Find callbacks for which all inputs are missing or in the exclusions
        const [included, excluded] = partition(({
            callback: { inputs },
            getInputs
        }) => all(isMultiValued, inputs) ||
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

    /*
        Return all callbacks with an `executionGroup` to allow group-processing
    */
    const executionGroup = Math.random().toString(16);
    return map(cb => ({
        ...cb,
        executionGroup
    }), callbacks);
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