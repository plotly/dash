import {
    concat,
    flatten,
    isEmpty,
    isNil,
    map,
    path,
    keys,
    pickBy,
    toPairs,
    pathOr
} from 'ramda';

import {ThunkDispatch} from 'redux-thunk';
import {AnyAction} from 'redux';

import {IStoreState} from '../store';

import {
    aggregateCallbacks,
    addRequestedCallbacks,
    removeExecutedCallbacks,
    addCompletedCallbacks,
    addStoredCallbacks
} from '../actions/callbacks';

import {parseIfWildcard} from '../actions/dependencies';

import {
    combineIdAndProp,
    getCallbacksByInput,
    getLayoutCallbacks,
    includeObservers
} from '../actions/dependencies_ts';

import {ICallback, IStoredCallback} from '../types/callbacks';

import {updateProps, setPaths, handleAsyncError} from '../actions';
import {getPath, computePaths, appendPaths} from '../actions/paths';
import {
    PatchAnalysis,
    analysisForAllProps,
    analysisForProp,
    tailAppendCount
} from '../actions/patchAnalysis';

import {applyPersistence, prunePersistence} from '../persistence';
import {IStoreObserverDefinition} from '../StoreObserver';

const observer: IStoreObserverDefinition<IStoreState> = {
    observer: ({dispatch, getState}) => {
        const {
            callbacks: {executed}
        } = getState();

        function applyProps(
            id: any,
            updatedProps: any,
            patchAnalysis?: PatchAnalysis
        ) {
            const {layout, paths} = getState();
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
            // A Patch resolves by carrying pre-existing children over from
            // Redux, user edits included, so applyPersistence must leave those
            // alone. It would otherwise see a "server override" and clear the
            // stored edit. The analysis says which components the patch really
            // created. Everything else came from a full replacement, where the
            // server returns fresh default values and persisted edits must be
            // restored (e.g. after a component moves on page).
            // Only the `children` prop matters here, that is the one
            // applyPersistence recurses through
            const {props} = applyPersistence(
                {props: updatedProps},
                dispatch,
                analysisForProp(patchAnalysis, 'children')
            );
            (dispatch as ThunkDispatch<any, any, AnyAction>)(
                updateProps({
                    itempath,
                    props,
                    source: 'response',
                    renderType: 'callback'
                })
            );

            return props;
        }

        let requestedCallbacks: ICallback[] = [];
        const storedCallbacks: IStoredCallback[] = [];

        executed.forEach(cb => {
            const predecessors = concat(cb.predecessors ?? [], [cb.callback]);

            const {
                callback: {clientside_function, output},
                executionResult
            } = cb;

            if (isNil(executionResult)) {
                return;
            }

            const {data, error, payload, patchedOutputs} = executionResult;

            if (data !== undefined) {
                Object.entries(data).forEach(
                    ([id, props]: [any, {[key: string]: any}]) => {
                        const parsedId = parseIfWildcard(id);
                        const {
                            graphs,
                            layout: oldLayout,
                            paths: oldPaths
                        } = getState();

                        // What the Patch operations of this output changed
                        const patchAnalysis = patchedOutputs?.[id];

                        // Components will trigger callbacks on their own as required (eg. derived)
                        const appliedProps = applyProps(
                            parsedId,
                            props,
                            patchAnalysis
                        );

                        // Add callbacks for modified inputs
                        requestedCallbacks = concat(
                            requestedCallbacks,
                            flatten(
                                map(
                                    prop =>
                                        getCallbacksByInput(
                                            graphs,
                                            oldPaths,
                                            parsedId,
                                            prop,
                                            true
                                        ),
                                    keys(props)
                                )
                            ).map(rcb => ({
                                ...rcb,
                                predecessors
                            }))
                        );

                        const basePath = getPath(oldPaths, parsedId);
                        if (!basePath) {
                            return;
                        }
                        const oldObj = path(basePath, oldLayout);

                        const childrenProps = pathOr(
                            'defaultValue',
                            [oldObj.namespace, oldObj.type],
                            (window as any).__dashprivate_childrenProps
                        );

                        const handlePaths = (
                            children: any,
                            oldChildren: any,
                            oldChildrenPath: any[],
                            filterRoot: any = false,
                            propAnalysis?: PatchAnalysis,
                            appendedCount = 0
                        ) => {
                            const oPaths = getState().paths;

                            // If this patch's only structural change was
                            // appending items to the tail (tracked by
                            // patchAnalysis.tailAppends), the pre-existing
                            // children kept their positions and identities.
                            // Compute paths only for the new tail slice
                            // instead of re-crawling the whole array - the
                            // dominant cost of a repeated Patch().append()
                            // into a large container.
                            const isTailAppend =
                                appendedCount > 0 &&
                                Array.isArray(children) &&
                                Array.isArray(oldChildren) &&
                                children.length ===
                                    oldChildren.length + appendedCount;

                            const paths = isTailAppend
                                ? appendPaths(
                                      children.slice(oldChildren.length),
                                      oldChildrenPath,
                                      oldChildren.length,
                                      oPaths
                                  )
                                : computePaths(
                                      children,
                                      oldChildrenPath,
                                      oPaths
                                  );
                            dispatch(setPaths(paths));

                            // Get callbacks for new layout (w/ execution group)
                            requestedCallbacks = concat(
                                requestedCallbacks,
                                getLayoutCallbacks(graphs, paths, children, {
                                    chunkPath: oldChildrenPath,
                                    patchAnalysis: propAnalysis,
                                    filterRoot
                                }).map(rcb => ({
                                    ...rcb,
                                    predecessors
                                }))
                            );

                            // Wildcard callbacks with array inputs (ALL / ALLSMALLER) need to trigger
                            // even due to the deletion of components.
                            // A tail append never removes anything, so oldChildren
                            // is unchanged and this pass can only find what it
                            // found last time (nothing new) - skip the crawl.
                            if (!isTailAppend) {
                                requestedCallbacks = concat(
                                    requestedCallbacks,
                                    getLayoutCallbacks(
                                        graphs,
                                        oldPaths,
                                        oldChildren,
                                        {
                                            removedArrayInputsOnly: true,
                                            newPaths: paths,
                                            chunkPath: oldChildrenPath,
                                            filterRoot
                                        }
                                    ).map(rcb => ({
                                        ...rcb,
                                        predecessors
                                    }))
                                );
                            }
                        };

                        let recomputed = false;

                        ['children']
                            .concat(childrenProps)
                            .forEach(childrenProp => {
                                if (recomputed) {
                                    return;
                                }
                                if (childrenProp.includes('[]')) {
                                    const [frontPath] = childrenProp
                                        .split('[]')
                                        .map(p => p.split('.').filter(e => e));

                                    const frontObj: any[] | undefined = path(
                                        frontPath,
                                        appliedProps
                                    );

                                    if (!frontObj) {
                                        return;
                                    }

                                    // Crawl layout needs the ns/type
                                    // This crawls every prop of the component at
                                    // once, so the analysis only applies if all
                                    // of them came from a Patch
                                    handlePaths(
                                        {
                                            ...oldObj,
                                            props: {
                                                ...oldObj.props,
                                                ...appliedProps
                                            }
                                        },
                                        oldObj,
                                        basePath,
                                        keys(appliedProps),
                                        analysisForAllProps(
                                            patchAnalysis,
                                            keys(props)
                                        )
                                    );
                                    // Only do it once for the component.
                                    recomputed = true;
                                } else {
                                    const childrenPropPath =
                                        childrenProp.split('.');
                                    const children = path(
                                        childrenPropPath,
                                        appliedProps
                                    );
                                    if (!children) {
                                        return;
                                    }

                                    const oldChildrenPath = concat(
                                        getPath(oldPaths, parsedId) as string[],
                                        ['props'].concat(childrenPropPath)
                                    );
                                    const oldChildren = path(
                                        oldChildrenPath,
                                        oldLayout
                                    );

                                    const childrenPropAnalysis =
                                        analysisForProp(
                                            patchAnalysis,
                                            childrenPropPath[0]
                                        );

                                    handlePaths(
                                        children,
                                        oldChildren,
                                        oldChildrenPath,
                                        false,
                                        childrenPropAnalysis,
                                        tailAppendCount(
                                            childrenPropAnalysis,
                                            childrenPropPath[0]
                                        )
                                    );
                                }
                            });

                        // persistence edge case: if you explicitly update the
                        // persistence key, other props may change that require us
                        // to fire additional callbacks
                        const addedProps = pickBy(
                            (_, k) => !(k in props),
                            appliedProps
                        );
                        if (!isEmpty(addedProps)) {
                            const {graphs: currentGraphs, paths} = getState();

                            requestedCallbacks = concat(
                                requestedCallbacks,
                                includeObservers(
                                    id,
                                    addedProps,
                                    currentGraphs,
                                    paths
                                ).map(rcb => ({
                                    ...rcb,
                                    predecessors
                                }))
                            );
                        }
                    }
                );

                // Add information about potentially updated outputs vs. updated outputs,
                // this will be used to drop callbacks from execution groups when no output
                // matching the downstream callback's inputs were modified
                storedCallbacks.push({
                    ...cb,
                    executionMeta: {
                        allProps: map(
                            combineIdAndProp,
                            flatten(cb.getOutputs(getState().paths))
                        ),
                        updatedProps: flatten(
                            map(
                                ([id, value]) =>
                                    map(
                                        property =>
                                            combineIdAndProp({id, property}),
                                        keys(value) as string[]
                                    ),
                                toPairs(data)
                            )
                        )
                    }
                });
            }

            if (error !== undefined) {
                let message;
                if (cb.callback.no_output) {
                    const inpts = keys(cb.changedPropIds).join(', ');
                    message = `Callback error with no output from input ${inpts}`;
                } else {
                    const outputs = payload
                        ? map(
                              combineIdAndProp,
                              flatten([payload.outputs])
                          ).join(', ')
                        : output;
                    message = `Callback error updating ${outputs}`;
                }
                if (clientside_function) {
                    const {namespace: ns, function_name: fn} =
                        clientside_function;
                    message += ` via clientside function ${ns}.${fn}`;
                }

                handleAsyncError(error, message, dispatch);

                storedCallbacks.push({
                    ...cb,
                    executionMeta: {
                        allProps: map(
                            combineIdAndProp,
                            flatten(cb.getOutputs(getState().paths))
                        ),
                        updatedProps: []
                    }
                });
            }
        });

        dispatch(
            aggregateCallbacks([
                executed.length ? removeExecutedCallbacks(executed) : null,
                executed.length ? addCompletedCallbacks(executed.length) : null,
                storedCallbacks.length
                    ? addStoredCallbacks(storedCallbacks)
                    : null,
                requestedCallbacks.length
                    ? addRequestedCallbacks(requestedCallbacks)
                    : null
            ])
        );
    },
    inputs: ['callbacks.executed']
};

export default observer;
