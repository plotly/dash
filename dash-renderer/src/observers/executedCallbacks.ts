import {
    concat,
    flatten,
    isEmpty,
    isNil,
    map,
    path,
    forEach,
    keys,
    has,
    pickBy,
    toPairs
} from 'ramda';

import { IStoreState } from '../store';

import {
    aggregateCallbacks,
    addRequestedCallbacks,
    removeExecutedCallbacks,
    addCompletedCallbacks,
    addStoredCallbacks,
    mutateOutput
} from '../actions/callbacks';

import { parseIfWildcard } from '../actions/dependencies';

import {
    combineIdAndProp,
    getCallbacksByInput,
    getLayoutCallbacks,
    includeObservers
} from '../actions/dependencies_ts';

import {
    ICallback,
    IStoredCallback
} from '../types/callbacks';

import { updateProps, setPaths, handleAsyncError } from '../actions';
import { getPath, computePaths } from '../actions/paths';

import {
    applyPersistence,
    prunePersistence
} from '../persistence';
import { IStoreObserverDefinition } from '../StoreObserver';

function getMutation(cbMutation: string | true | undefined, outputProp: any) : string | undefined {
    const isMutation = outputProp?.__dashprivate_mutation;
    const mutation = outputProp?.mutation;

    // Error: `__dashprivate_mutation` must be nil or true
    if (!isNil(isMutation) && isMutation !== true) {
        throw Error(`Callback returned a mutation operation with property "__dashprivate_mutation" that isn't true.`);
    }

    // Error: `mutation` must be a string
    if (isMutation && typeof mutation !== 'string') {
        throw Error(`Callback returned a mutation operation with property "mutation" that isn't a string.`);
    }

    // Error: Callback ouptut does not allow mutations but the output value is a mutation
    if (isMutation && isNil(cbMutation)) {
        throw Error(`Callback returned a mutation operation on a non-mutation callback property.`);
    }

    if (isNil(cbMutation)) {
        return;
    }

    if (cbMutation === true) {
        if (!mutation) {
            throw Error(`Callback returned a value but the callback does not allow non-mutation results`);
        }

        return mutation;
    } else {
        return isMutation ? mutation : cbMutation;
    }
}

function getValue(outputProp: any) {
    return outputProp?.__dashprivate_mutation ? outputProp?.output : outputProp;
}

function mutateOutputProps(id: any, props: { [key: string]: any }, cb: ICallback, getState: () => IStoreState) {
    const { layout, paths } = getState();
    const itempath = getPath(paths, id);
    if (!itempath) {
        return props;
    }

    // mutate output props
    forEach(key => {
        const cbp = cb.callback.outputs.find(o => o.property === key);
        if (!cbp) {
            return;
        }

        props[key] = mutateOutput(
            getMutation(cbp.mutation, props[key]),
            getValue(props[key]),
            (path(itempath, layout) as any).props[key]
        )
    }, keys(props));

    return props;
}

const observer: IStoreObserverDefinition<IStoreState> = {
    observer: ({
        dispatch,
        getState
    }) => {
        const {
            callbacks: {
                executed
            }
        } = getState();

        function applyProps(id: any, updatedProps: any) {
            const { layout, paths } = getState();
            const itempath = getPath(paths, id);
            if (!itempath) {
                return false;
            }

            // This is a callback-generated update.
            // Check if this invalidates existing persisted prop values,
            // or if persistence changed, whether this updates other props.
            updatedProps = prunePersistence(
                path(itempath, layout),
                updatedProps,
                dispatch
            );

            // In case the update contains whole components, see if any of
            // those components have props to update to persist user edits.
            const { props } = applyPersistence({ props: updatedProps }, dispatch);

            dispatch(
                updateProps({
                    itempath,
                    props,
                    source: 'response'
                })
            );

            return props;
        }

        let requestedCallbacks: ICallback[] = [];
        let storedCallbacks: IStoredCallback[] = [];

        forEach(cb => {
            const predecessors = concat(
                cb.predecessors ?? [],
                [cb.callback]
            );

            const {
                callback: {
                    clientside_function,
                    output
                },
                executionResult
            } = cb;

            if (isNil(executionResult)) {
                return;
            }

            const { data, error, payload } = executionResult;

            if (data !== undefined) {
                forEach(([id, props]: [any, { [key: string]: any }]) => {
                    props = mutateOutputProps(id, props, cb, getState);

                    const parsedId = parseIfWildcard(id);
                    const { graphs, layout: oldLayout, paths: oldPaths } = getState();

                    // Components will trigger callbacks on their own as required (eg. derived)
                    const appliedProps = applyProps(parsedId, props);

                    // Add callbacks for modified inputs
                    requestedCallbacks = concat(
                        requestedCallbacks,
                        flatten(map(
                            prop => getCallbacksByInput(graphs, oldPaths, parsedId, prop, true),
                            keys(props)
                        )).map(rcb => ({
                            ...rcb,
                            predecessors
                        }))
                    );

                    // New layout - trigger callbacks for that explicitly
                    if (has('children', appliedProps)) {
                        const { children } = appliedProps;

                        const oldChildrenPath: string[] = concat(getPath(oldPaths, parsedId) as string[], ['props', 'children']);
                        const oldChildren = path(oldChildrenPath, oldLayout);

                        const paths = computePaths(children, oldChildrenPath, oldPaths);
                        dispatch(setPaths(paths));

                        // Get callbacks for new layout (w/ execution group)
                        requestedCallbacks = concat(
                            requestedCallbacks,
                            getLayoutCallbacks(graphs, paths, children, {
                                chunkPath: oldChildrenPath
                            }).map(rcb => ({
                                ...rcb,
                                predecessors
                            }))
                        );

                        // Wildcard callbacks with array inputs (ALL / ALLSMALLER) need to trigger
                        // even due to the deletion of components
                        requestedCallbacks = concat(
                            requestedCallbacks,
                            getLayoutCallbacks(graphs, oldPaths, oldChildren, {
                                removedArrayInputsOnly: true, newPaths: paths, chunkPath: oldChildrenPath
                            }).map(rcb => ({
                                ...rcb,
                                predecessors
                            }))
                        );
                    }

                    // persistence edge case: if you explicitly update the
                    // persistence key, other props may change that require us
                    // to fire additional callbacks
                    const addedProps = pickBy(
                        (_, k) => !(k in props),
                        appliedProps
                    );
                    if (!isEmpty(addedProps)) {
                        const { graphs: currentGraphs, paths } = getState();

                        requestedCallbacks = concat(
                            requestedCallbacks,
                            includeObservers(id, addedProps, currentGraphs, paths).map(rcb => ({
                                ...rcb,
                                predecessors
                            }))
                        );
                    }
                }, Object.entries(data));

                // Add information about potentially updated outputs vs. updated outputs,
                // this will be used to drop callbacks from execution groups when no output
                // matching the downstream callback's inputs were modified
                storedCallbacks.push({
                    ...cb,
                    executionMeta: {
                        allProps: map(combineIdAndProp, flatten(cb.getOutputs(getState().paths))),
                        updatedProps: flatten(map(
                            ([id, value]) => map(
                                property => combineIdAndProp({ id, property }),
                                keys(value)
                            ),
                            toPairs(data)
                        ))
                    }
                });
            }

            if (error !== undefined) {
                const outputs = payload
                    ? map(combineIdAndProp, flatten([payload.outputs])).join(', ')
                    : output;
                let message = `Callback error updating ${outputs}`;
                if (clientside_function) {
                    const { namespace: ns, function_name: fn } = clientside_function;
                    message += ` via clientside function ${ns}.${fn}`;
                }

                handleAsyncError(error, message, dispatch);

                storedCallbacks.push({
                    ...cb,
                    executionMeta: {
                        allProps: map(combineIdAndProp, flatten(cb.getOutputs(getState().paths))),
                        updatedProps: []
                    }
                });
            }
        }, executed);

        dispatch(aggregateCallbacks([
            executed.length ? removeExecutedCallbacks(executed) : null,
            executed.length ? addCompletedCallbacks(executed.length) : null,
            storedCallbacks.length ? addStoredCallbacks(storedCallbacks) : null,
            requestedCallbacks.length ? addRequestedCallbacks(requestedCallbacks) : null
        ]));
    },
    inputs: ['callbacks.executed']
};

export default observer;
