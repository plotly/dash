import { DepGraph } from 'dependency-graph';
// import isNumeric from 'fast-isnumeric';
import {
    evolve,
    map,
    forEach,
    partition,
    keys,
    concat,
    // values,
    // pipe,
    // flatten,
    // filter,
    // both,
    // propIs,
    // propSatisfies,
    // complement,
    // isEmpty,
    // reduce,
    forEachObjIndexed,
    unnest,
    difference
    // isNil
} from 'ramda';
import { createAction } from 'redux-actions';

import { DependencyGraphActionType } from '../reducers/graphs';
import { ICallbackDefinition, ICallbackProperty, ILayoutCallbackProperty, IWildcardCallbackId } from '../types/callbacks';
import { validateDependencies } from './computeMaps';
// import { idValSort } from './dependencies';
import { parseIfWildcard, combineIdAndProp } from './dependencies_ts';

type DispatchError = (message: string, lines: string[]) => void;
type IResolvedCallbackProperty = Omit<ICallbackProperty, 'id'> & Pick<ILayoutCallbackProperty, 'id'>;
type IResolvedCallback = Omit<Omit<Omit<ICallbackDefinition, 'inputs'>, 'outputs'>, 'state'> & {
    inputs: IResolvedCallbackProperty[],
    outputs: IResolvedCallbackProperty[],
    state: IResolvedCallbackProperty[]
};

interface ICallbackEntry {
    [key: string]: [IResolvedCallback, IResolvedCallbackProperty][];
}

interface ICallbackMap {
    [key: string]: ICallbackEntry;
}

// interface IWildcardUsageEntry {
//     exact: any[];
//     expand: number;
//     vals?: any[]
// }

// interface IWildcardUsage {
//     [key: string]: IWildcardUsageEntry;
// }

const fixId = evolve({ id: parseIfWildcard }) as (cbp: ICallbackProperty) => IResolvedCallbackProperty;
const fixIds = map(fixId);

const getResolvedCallbacks = map(evolve({
    inputs: fixIds,
    outputs: fixIds,
    state: fixIds
})) as (callbacks: ICallbackDefinition[]) => IResolvedCallback[];

// const getWildcardCallbackProperties = pipe(
//     map(({ inputs, outputs }: IResolvedCallback) => concat(inputs, outputs)),
//     flatten,
//     filter(both(
//         propIs('Object', 'id'),
//         propSatisfies(complement(isEmpty), 'id')
//     )),
//     map(cbp => cbp.id)
// ) as unknown as (callbacks: IResolvedCallback[]) => IWildcardCallbackId[];


// /**
//  * Identify all exact and ALLSMALLER wildcards usage for all props
//  */
// const getWildcardDirectUsage = reduce((acc, id: IWildcardCallbackId) => {
//     forEachObjIndexed((val: any, key) => {
//         acc[key] = acc[key] ?? { exact: [], expand: 0 };

//         if (!val.wild) {
//             acc[key].exact.push(val);
//         } else if (val.expand) {
//             ++acc[key].expand;
//         }
//     }, id);

//     return acc;
// }, {} as IWildcardUsage);

// const getWildcardAssumedUsage = (usage: IWildcardUsage) => reduce((acc, entry) => {
//     const { exact, expand } = entry;
//     const vals = exact.slice().sort(idValSort);
//     if (expand) {
//         for (let i = 0; i < expand; i++) {
//             if (exact.length) {
//                 vals.unshift(valBefore(vals[0]));
//                 vals.push(valAfter(vals[vals.length - 1]));
//             } else {
//                 vals.push(i);
//             }
//         }
//     } else if (!exact.length) {
//         // only MATCH/ALL - still need a value
//         vals.push(0);
//     }

//     entry.vals = vals;

//     return acc;
// }, usage, values(usage));

// const getWildcardUsage = pipe(getWildcardCallbackProperties, getWildcardDirectUsage, getWildcardAssumedUsage);

/*
 * Provide a value known to be before or after v, according to idValSort
 */
// const valBefore = (v: any) => (isNumeric(v) ? v - 1 : 0);
// const valAfter = (v: any) => (typeof v === 'string' ? v + 'z' : 'z');

const push = (
    target: ICallbackEntry,
    key: string,
    value: [IResolvedCallback, IResolvedCallbackProperty]
) => (target[key] = target[key] || []).push(value);

export default (
    callbacks: ICallbackDefinition[],
    dispatchError: DispatchError
): DepGraph<any> => {
    console.log('expComputeGraph > eval');
    const resolvedCallbacks = getResolvedCallbacks(callbacks);

    if (!validateDependencies(resolvedCallbacks, dispatchError)) {
        return new DepGraph();
    }

    // const wildcardUsage = getWildcardUsage(resolvedCallbacks);

    const callbackMap: ICallbackMap = {
        inputs: {},
        standardOutputs: {},
        mutationOutputs: {}
    };

    // Create inputs, standardOutputs, mutationOutputs mapping
    forEach(cb => {
        const [
            mutationOutputs,
            standardOutputs
        ] = partition(output => !!output.mutation, cb.outputs);

        forEach(cbp => push(callbackMap.inputs, combineIdAndProp(cbp), [cb, cbp]), cb.inputs);
        forEach(cbp => push(callbackMap.mutationOutputs, combineIdAndProp(cbp), [cb, cbp]), mutationOutputs);
        forEach(cbp => push(callbackMap.standardOutputs, combineIdAndProp(cbp), [cb, cbp]), standardOutputs);
    }, resolvedCallbacks);

    const graphs = new DepGraph();

    forEach(cb => {
        graphs.addNode(cb.output, cb);
    }, resolvedCallbacks);

    // Create links between the output and inputs
    forEach(cb => {
        const [
            wildMutationOutputs,
            fixedMutationOutputs,
            wildStandardOutputs,
            fixedStandardOutputs
        ] = unnest(map(
            partition(output => typeof output.id === 'object'),
            partition<IResolvedCallbackProperty>(output => !!output.mutation, cb.outputs)
        ));

        forEach(cbp => {
            const idKey = combineIdAndProp(cbp);
            const affected = concat(
                callbackMap.inputs[idKey] || [],
                callbackMap.mutationOutputs[idKey] || []
            );

            forEach(([target, _targetCallbackProperty]) => {
                graphs.addDependency(cb.output, target.output);
            }, affected);
        }, fixedStandardOutputs);

        forEach(cbp => {
            const idKey = combineIdAndProp(cbp);
            const affected = callbackMap.inputs[idKey] || [];

            forEach(([target, _targetCallbackProperty]) => {
                graphs.addDependency(cb.output, target.output);
            }, affected);
        }, fixedMutationOutputs);

        forEach(cbp => {
            const idKey = combineIdAndProp(cbp);
            const affected = concat(
                callbackMap.inputs[idKey] || [],
                callbackMap.mutationOutputs[idKey] || []
            );

            const fKeys = keys(cbp.id);

            forEach(([tcb, tcbp]) => {
                const tKeys = keys(tcbp.id);

                if (tKeys.length !== fKeys.length || difference(tKeys, fKeys).length) {
                    return;
                }

                forEachObjIndexed((fValue, fKey) => {
                    const tValue = (cbp.id as IWildcardCallbackId)[fKey];

                    if (fValue === tValue || typeof fValue === 'object' || typeof tValue === 'object') {
                        graphs.addDependency(cb.output, tcb.output);
                    }

                }, cbp.id as IWildcardCallbackId);
            }, affected);
        }, wildStandardOutputs);

        forEach(cbp => {
            const idKey = combineIdAndProp(cbp);
            const affected = callbackMap.inputs[idKey] || [];

            const fKeys = keys(cbp.id);

            forEach(([tcb, tcbp]) => {
                const tKeys = keys(tcbp.id);

                if (tKeys.length !== fKeys.length || difference(tKeys, fKeys).length) {
                    return;
                }

                forEachObjIndexed((fValue, fKey) => {
                    const tValue = (cbp.id as IWildcardCallbackId)[fKey];

                    if (fValue === tValue || typeof fValue === 'object' || typeof tValue === 'object') {
                        graphs.addDependency(cb.output, tcb.output);
                    }

                }, cbp.id as IWildcardCallbackId);
            }, affected);
        }, wildMutationOutputs);
    }, resolvedCallbacks);

    return graphs;
}

export const setGraph = createAction<DepGraph<any>>(DependencyGraphActionType.Set);
