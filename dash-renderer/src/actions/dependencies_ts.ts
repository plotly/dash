import {
    all,
    assoc,
    call,
    concat,
    difference,
    F,
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
    reduce,
    zipObj
} from 'ramda';
import callbacks from '../reducers/callbacks';
import {
    ICallback,
    ICallbackProperty,
    ICallbackDefinition,
    ILayoutCallbackProperty,
    ICallbackTemplate
} from '../types/callbacks';
import {
    addAllResolvedFromOutputs,
    splitIdAndProp,
    stringifyId,
    getUnfilteredLayoutCallbacks,
    isMultiValued,
    idMatch
} from './dependencies';
import {getPath} from './paths';

export const DIRECT = 2;
export const INDIRECT = 1;
export const mergeMax = mergeWith(Math.max);

export const combineIdAndProp = ({id, property}: ICallbackProperty) =>
    `${stringifyId(id)}.${property}`;

// for everycallback returned,
// check if the relevant callback is in the callback path of the thing

//TODO: override the interface for this, compare the signatures
function isSimilar(paths:any, callbackA:ICallback, callbackB:ICallback):boolean{
    
    const outputsA = flatten(callbackA.getOutputs(paths));
    const inputsA = flatten(callbackA.getInputs(paths));

    const outputsB = flatten(callbackB.getOutputs(paths));
    const inputsB = flatten(callbackB.getInputs(paths));

    return (JSON.stringify(inputsA)==JSON.stringify(inputsB) && JSON.stringify(outputsA)&&JSON.stringify(outputsB)) ? true: false;
}

export function callbackPathExists(graphs:any, paths:any, fromCallback:ICallback, toCallback:ICallback): boolean {

    // check for base condition
    if (isSimilar(paths, fromCallback, toCallback)) {
        console.log('CALLDAG:callbackPathExists match found');
        return true;
    }

    const outputs = flatten(fromCallback.getOutputs(paths));
    console.log('CALLDAG:callbackPathExists outputs', outputs);

    const callbacks =
        flatten(map(
            ({id, property}: any) => {
                return graphs.inputMap[id][property];
            },
            outputs
        ))

    if (!callbacks.length){
        //we have reached the end of the DAG
        return false;
    }

    const matches: ICallback[] = [];
    callbacks.forEach(
        addAllResolvedFromOutputs(resolveDeps(), paths, matches)
    );

    const exists = matches.some((cb)=>{return callbackPathExists(graphs, paths, cb, toCallback)})
    console.log('CALLDAG:callbackPathExists callbacks',exists);
    return exists;
}

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

    console.log("CALLDAG:getCallBackByInput:inputs ID", id, "PROP", prop);

    if (typeof id === 'string') {
        // standard id version
        const callbacks = (graphs.inputMap[id] || {})[prop];
        if (!callbacks) {
            return [];
        }

        console.log("CALLDAG:getCallBackByInput callbacks", callbacks);

        callbacks.forEach(
            addAllResolvedFromOutputs(resolveDeps(), paths, matches)
        );

        console.log("CALLDAG:getCallBackByInput callbacks afterOutputs", callbacks, "matches", matches);
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

    console.log("CALLDAG:getCallBackByInput callbacks matches with priority", matches);
    
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
    let touchedOutputs: {[key: string]: boolean} = {};
    const priority: number[] = [];

    while (callbacks.length) {
        const outputs = filter(
            o => !touchedOutputs[combineIdAndProp(o)],
            flatten(map(cb => flatten(cb.getOutputs(paths)), callbacks))
        );

        touchedOutputs = reduce(
            (touched, o) => assoc(combineIdAndProp(o), true, touched),
            touchedOutputs,
            outputs
        );

        console.log("CALLDAG:getPriority callback outputs", outputs);

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
        console.log("CALLDAG:getPriority callbacks after flattening", callbacks);

        if (callbacks.length) {
            priority.push(callbacks.length);
        }
    }

    priority.unshift(priority.length);

    return map(i => Math.min(i, 35).toString(36), priority).join('');
}

export const getReadyCallbacks = (
    paths: any,
    candidates: ICallback[],
    callbacks: ICallback[] = candidates
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
    const outputsMap: {[key: string]: boolean} = {};
    forEach(output => (outputsMap[output] = true), outputs);

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
    

    console.log('CALLDAG:includeObservers properties', properties, keys(properties));

    let func = (propName)=>{
            let cbs = getCallbacksByInput(graphs, paths, id, propName);
            console.log("CALLDAG:includeObservers callback", cbs);
            return cbs;
    }

    const flattenedCbs = flatten(
        map(
            (propName)=> func(propName),
            keys(properties)
        )
    );

    var validCbs = [... flattenedCbs];

    //TODO: not sure if this is optimal
    // for(let i=0; i<validCbs.length; i++) {
    //     for (let j=i+1; j<validCbs.length; j++) {
    //         if (callbackPathExists(graphs, paths, validCbs[i], flattenedCbs[j])) {
    //             //path exists remove the extra cb
    //             validCbs.splice(j,1);
    //         }
    //     }
    // }

    console.log('CALLDAG:includeObservers: validCbs', validCbs);

    return validCbs;

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

    const added = map(
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
    return (paths: any) => ({id: idPattern, property}: ICallbackProperty) => {
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
