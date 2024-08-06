import {
    all,
    assoc,
    concat,
    difference,
    filter,
    flatten,
    isEmpty,
    keys,
    map,
    mergeWith,
    partition,
    path,
    pickBy,
    props,
    reduce,
    zipObj
} from 'ramda';
import {
    ICallback,
    ICallbackDefinition,
    ICallbackProperty,
    ICallbackTemplate,
    ILayoutCallbackProperty
} from '../types/callbacks';
import {
    addAllResolvedFromOutputs,
    getUnfilteredLayoutCallbacks,
    idMatch,
    isMultiValued,
    splitIdAndProp,
    stringifyId
} from './dependencies';
import {getPath} from './paths';

export const DIRECT = 2;
export const INDIRECT = 1;
export const mergeMax = mergeWith(Math.max);

export const combineIdAndProp = ({id, property}: ICallbackProperty) =>
    `${stringifyId(id)}.${property}`;

export function getCallbacksByInput(
    graphs: any,
    paths: any,
    id: any,
    prop: any,
    changeType?: any,
    withPriority = true
): ICallback[] {
    const matches: ICallback[] = [];
    const idAndProp = combineIdAndProp({id, property: prop});

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
        const _keys = Object.keys(id).sort();
        const vals = props(_keys, id);
        const keyStr = _keys.join(',');
        const patterns: any[] = (graphs.inputPatterns[keyStr] || {})[prop];
        if (!patterns) {
            return [];
        }
        patterns.forEach(pattern => {
            if (idMatch(_keys, vals, pattern.values)) {
                pattern.callbacks.forEach(
                    addAllResolvedFromOutputs(
                        resolveDeps(_keys, vals, pattern.values),
                        paths,
                        matches
                    )
                );
            }
        });
    }
    matches.forEach(match => {
        match.changedPropIds[idAndProp] = changeType || DIRECT;
        if (withPriority) {
            match.priority = getPriority(graphs, paths, match);
        }
    });
    return matches;
}

/*
 * Builds a tree of all callbacks that can be triggered by the provided callback.
 * Uses the number of callbacks at each tree depth and the total depth of the tree
 * to create a sortable priority hash.
 */
export function getPriority(
    graphs: any,
    paths: any,
    callback: ICallback
): string {
    let callbacks: ICallback[] = [callback];
    const touchedOutputs: {[key: string]: boolean} = {};
    const touchedCbIds: {[key: string]: boolean} = {};
    const priority: number[] = [];

    while (callbacks.length) {
        callbacks = filter(c => {
            const touched = touchedCbIds[c.resolvedId];
            touchedCbIds[c.resolvedId] = true;
            return touched;
        }, callbacks);

        const outputs = filter(
            o => !touchedOutputs[combineIdAndProp(o)],
            flatten(map(cb => flatten(cb.getOutputs(paths)), callbacks))
        );

        outputs.forEach(o => (touchedOutputs[combineIdAndProp(o)] = true));

        callbacks = flatten(
            map(
                ({id, property}: any) =>
                    getCallbacksByInput(
                        graphs,
                        paths,
                        id,
                        property,
                        INDIRECT,
                        false
                    ),
                outputs
            )
        );

        if (callbacks.length) {
            priority.push(callbacks.length);
        }
    }

    priority.unshift(priority.length);

    return map(i => Math.min(i, 35).toString(36), priority).join('');
}

export function getAllSubsequentOutputsForCallback(
    graphs: any,
    paths: any,
    callback: ICallback
) {
    let callbacks: ICallback[] = [callback];
    let touchedOutputs: {[key: string]: boolean} = {};

    // this traverses the graph all the way to the end
    while (callbacks.length) {
        // don't add it if it already exists based on id and props
        const outputs = filter(
            o => !touchedOutputs[combineIdAndProp(o)],
            flatten(map(cb => flatten(cb.getOutputs(paths)), callbacks))
        );

        touchedOutputs = reduce(
            (touched, o) => assoc(combineIdAndProp(o), true, touched),
            touchedOutputs,
            outputs
        );

        callbacks = flatten(
            map(
                ({id, property}: any) =>
                    getCallbacksByInput(
                        graphs,
                        paths,
                        id,
                        property,
                        INDIRECT,
                        false
                    ),
                outputs
            )
        );
    }

    return touchedOutputs;
}

export const getReadyCallbacks = (
    paths: any,
    candidates: ICallback[],
    callbacks: ICallback[] = candidates,
    graphs: any = {}
): ICallback[] => {
    // Skip if there's no candidates
    if (!candidates.length) {
        return [];
    }

    // Find all outputs of all active callbacks
    const outputs = map(
        combineIdAndProp,
        reduce<ICallback, any[]>(
            (o, cb) => concat(o, flatten(cb.getOutputs(paths))),
            [],
            callbacks
        )
    );

    // Make `outputs` hash table for faster access
    let outputsMap: {[key: string]: boolean} = {};
    outputs.forEach(output => (outputsMap[output] = true));

    // find all the outputs touched by activeCallbacks
    // remove this check if graph is accessible all the time

    if (Object.keys(graphs).length) {
        //not sure if graph will be accessible all the time
        const allTouchedOutputs: {[key: string]: boolean}[] = flatten(
            map(
                cb => getAllSubsequentOutputsForCallback(graphs, paths, cb),
                callbacks
            )
        );

        // overrrides the outputsMap, will duplicate callbacks filtered
        // this is only done to silence typescript errors
        if (allTouchedOutputs.length > 0) {
            outputsMap = Object.assign(
                allTouchedOutputs[0],
                ...allTouchedOutputs
            );
        }
    }

    // Find `requested` callbacks that do not depend on a outstanding output (as either input or state)
    // Outputs which overlap an input do not count as an outstanding output
    return filter(
        cb =>
            all<ILayoutCallbackProperty>(
                cbp => !outputsMap[combineIdAndProp(cbp)],
                difference(
                    flatten(cb.getInputs(paths)),
                    flatten(cb.getOutputs(paths))
                )
            ),
        candidates
    );
};

export const getLayoutCallbacks = (
    graphs: any,
    paths: any,
    layout: any,
    options: any
): ICallback[] => {
    let exclusions: string[] = [];
    let callbacks = getUnfilteredLayoutCallbacks(
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

        Further exclusion might happen after callbacks return with:
        - PreventUpdate
        - no_update
    */
    while (true) {
        // Find callbacks for which all inputs are missing or in the exclusions
        const [included, excluded] = partition(
            ({callback: {inputs}, getInputs}) =>
                all(isMultiValued, inputs) ||
                !isEmpty(
                    difference(
                        map(combineIdAndProp, flatten(getInputs(paths))),
                        exclusions
                    )
                ),
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
            map(
                combineIdAndProp,
                flatten(map(({getOutputs}) => getOutputs(paths), excluded))
            )
        );
    }

    if (options.filterRoot) {
        let rootId = path(['props', 'id'], layout);
        if (rootId) {
            rootId = stringifyId(rootId);
            // Filter inputs that are not present in the response
            callbacks = callbacks.filter(cb =>
                cb.callback.inputs.reduce(
                    (previous: any, input: any) =>
                        previous ||
                        (stringifyId(input.id) == rootId &&
                            options.filterRoot.includes(input.property)),
                    false
                )
            );
        }
    }

    /*
        Return all callbacks with an `executionGroup` to allow group-processing
    */
    const executionGroup = Math.random().toString(16);
    return map(cb => ({...cb, executionGroup}), callbacks);
};

export const getUniqueIdentifier = ({
    anyVals,
    callback: {inputs, outputs, state}
}: ICallback): string =>
    concat(
        map(combineIdAndProp, [...inputs, ...outputs, ...state]),
        Array.isArray(anyVals) ? anyVals : anyVals === '' ? [] : [anyVals]
    ).join(',');

export function includeObservers(
    id: any,
    properties: any,
    graphs: any,
    paths: any
): ICallback[] {
    return flatten(
        map(
            propName => getCallbacksByInput(graphs, paths, id, propName),
            keys(properties)
        )
    );
}

/*
 * Create a pending callback object. Includes the original callback definition,
 * its resolved ID (including the value of all MATCH wildcards),
 * accessors to find all inputs, outputs, and state involved in this
 * callback (lazy as not all users will want all of these).
 */
export const makeResolvedCallback = (
    callback: ICallbackDefinition,
    resolve: (_: any) => (_: ICallbackProperty) => ILayoutCallbackProperty[],
    anyVals: any[] | string
): ICallbackTemplate => ({
    callback,
    anyVals,
    resolvedId: callback.output + anyVals,
    getOutputs: paths => callback.outputs.map(resolve(paths)),
    getInputs: paths => callback.inputs.map(resolve(paths)),
    getState: paths => callback.state.map(resolve(paths)),
    changedPropIds: {},
    initialCall: false
});

export function pruneCallbacks<T extends ICallback>(
    callbacks: T[],
    paths: any
): {
    added: T[];
    removed: T[];
} {
    const [, removed] = partition(
        ({getOutputs, callback: {outputs}}) =>
            flatten(getOutputs(paths)).length === outputs.length,
        callbacks
    );

    const [, modified] = partition(
        ({getOutputs}) => !flatten(getOutputs(paths)).length,
        removed
    );

    const added: any = map(
        cb =>
            assoc(
                'changedPropIds',
                pickBy(
                    (_, propId) => getPath(paths, splitIdAndProp(propId).id),
                    cb.changedPropIds
                ),
                cb
            ),
        modified
    );

    return {
        added,
        removed
    };
}

export function resolveDeps(
    refKeys?: any,
    refVals?: any,
    refPatternVals?: string
) {
    return (paths: any) =>
        ({id: idPattern, property}: ICallbackProperty) => {
            if (typeof idPattern === 'string') {
                const path = getPath(paths, idPattern);
                return path ? [{id: idPattern, property, path}] : [];
            }
            const _keys = Object.keys(idPattern).sort();
            const patternVals = props(_keys, idPattern);
            const keyStr = _keys.join(',');
            const keyPaths = paths.objs[keyStr];
            if (!keyPaths) {
                return [];
            }
            const result: ILayoutCallbackProperty[] = [];
            keyPaths.forEach(({values: vals, path}: any) => {
                if (
                    idMatch(
                        _keys,
                        vals,
                        patternVals,
                        refKeys,
                        refVals,
                        refPatternVals
                    )
                ) {
                    result.push({id: zipObj(_keys, vals), property, path});
                }
            });
            return result;
        };
}
