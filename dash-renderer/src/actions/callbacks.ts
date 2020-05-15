import {
    concat,
    flatten,
    keys,
    map,
    mergeDeepRight,
    path,
    pick,
    pluck,
    zip,
} from 'ramda';

import { STATUS } from '../constants/constants';
import { ICallback, CallbackResult, IExecutingCallback, CallbackActionType, IExecutedCallback, CallbackAggregateActionType } from "../reducers/callbacks";
import { isMultiValued, stringifyId, isMultiOutputProp } from './dependencies';
import { urlBase } from './utils';
import { getCSRFHeader } from '.';
import { createAction, Action } from 'redux-actions';

export const setPendingCallbacks = createAction<ICallback[]>('SET_PENDING_CALLBACKS');

export const addCompletedCallbacks = createAction<number>(
    CallbackAggregateActionType.AddCompleted
);
export const addExecutedCallbacks = createAction<IExecutedCallback[]>(
    CallbackActionType.AddExecuted
);
export const addExecutingCallbacks = createAction<IExecutingCallback[]>(
    CallbackActionType.AddExecuting
);
export const addPrioritizedCallbacks = createAction<ICallback[]>(
    CallbackActionType.AddPrioritized
);
export const addRequestedCallbacks = createAction<ICallback[]>(
    CallbackActionType.AddRequested
);
export const addWatchedCallbacks = createAction<IExecutingCallback[]>(CallbackActionType.AddWatched);
export const removeExecutedCallbacks = createAction(
    CallbackActionType.RemoveExecuted
);
export const removeExecutingCallbacks = createAction<IExecutingCallback[]>(
    CallbackActionType.RemoveExecuting
);
export const removePrioritizedCallbacks = createAction<ICallback[]>(
    CallbackActionType.RemovePrioritized
);
export const removeRequestedCallbacks = createAction<ICallback[]>(
    CallbackActionType.RemoveRequested
);
export const removeWatchedCallbacks = createAction<IExecutingCallback[]>(
    CallbackActionType.RemoveWatched
);
export const aggregateCallbacks = createAction<(
    Action<ICallback[]> |
    Action<number> |
    null
)[]>(CallbackAggregateActionType.Aggregate);

function unwrapIfNotMulti(
    paths: any,
    idProps: any,
    spec: any,
    anyVals: any,
    depType: any
) {
    let msg = '';

    if (isMultiValued(spec)) {
        return [idProps, msg];
    }

    if (idProps.length !== 1) {
        if (!idProps.length) {
            const isStr = typeof spec.id === 'string';
            msg =
                'A nonexistent object was used in an `' +
                depType +
                '` of a Dash callback. The id of this object is ' +
                (isStr
                    ? '`' + spec.id + '`'
                    : JSON.stringify(spec.id) +
                    (anyVals ? ' with MATCH values ' + anyVals : '')) +
                ' and the property is `' +
                spec.property +
                (isStr
                    ? '`. The string ids in the current layout are: [' +
                    keys(paths.strs).join(', ') +
                    ']'
                    : '`. The wildcard ids currently available are logged above.');
        } else {
            msg =
                'Multiple objects were found for an `' +
                depType +
                '` of a callback that only takes one value. The id spec is ' +
                JSON.stringify(spec.id) +
                (anyVals ? ' with MATCH values ' + anyVals : '') +
                ' and the property is `' +
                spec.property +
                '`. The objects we found are: ' +
                JSON.stringify(map(pick(['id', 'property']), idProps));
        }
    }
    return [idProps[0], msg];
}

function fillVals(
    paths: any,
    layout: any,
    cb: ICallback,
    specs: any,
    depType: any,
    allowAllMissing: boolean = false
) {
    const getter = depType === 'Input' ? cb.getInputs : cb.getState;
    const errors: any[] = [];
    let emptyMultiValues = 0;

    const inputVals = getter(paths).map((inputList: any, i: number) => {
        const [inputs, inputError] = unwrapIfNotMulti(
            paths,
            inputList.map(({ id, property, path: path_ }: any) => ({
                id,
                property,
                value: (path(path_, layout) as any).props[property],
            })),
            specs[i],
            cb.anyVals,
            depType
        );
        if (isMultiValued(specs[i]) && !inputs.length) {
            emptyMultiValues++;
        }
        if (inputError) {
            errors.push(inputError);
        }
        return inputs;
    });

    if (errors.length) {
        if (
            allowAllMissing &&
            errors.length + emptyMultiValues === inputVals.length
        ) {
            // We have at least one non-multivalued input, but all simple and
            // multi-valued inputs are missing.
            // (if all inputs are multivalued and all missing we still return
            // them as normal, and fire the callback.)
            return null;
        }
        // If we get here we have some missing and some present inputs.
        // Or all missing in a context that doesn't allow this.
        // That's a real problem, so throw the first message as an error.
        refErr(errors, paths);
    }

    return inputVals;
}

function refErr(errors: any, paths: any) {
    const err = errors[0];
    if (err.indexOf('logged above') !== -1) {
        // Wildcard reference errors mention a list of wildcard specs logged
        // TODO: unwrapped list of wildcard ids?
        // eslint-disable-next-line no-console
        console.error(paths.objs);
    }
    throw new ReferenceError(err);
}

const getVals = (input: any) =>
    Array.isArray(input) ? pluck('value', input) : input.value;

const zipIfArray = (a: any, b: any) => (Array.isArray(a) ? zip(a, b) : [[a, b]]);

export function executeCallback(
    cb: ICallback,
    config: any,
    hooks: any,
    paths: any,
    layout: any,
    { allOutputs }: any
): IExecutingCallback {
    const { output, inputs, state, clientside_function } = cb.callback;

    try {
        const inVals = fillVals(paths, layout, cb, inputs, 'Input', true);

        /* Prevent callback if there's no inputs */
        if (inVals === null) {
            return {
                ...cb,
                executionPromise: null
            };
        }

        const outputs: any[] = [];
        const outputErrors: any[] = [];
        allOutputs.forEach((out: any, i: number) => {
            const [outi, erri] = unwrapIfNotMulti(
                paths,
                map(pick(['id', 'property']), out),
                cb.callback.outputs[i],
                cb.anyVals,
                'Output'
            );
            outputs.push(outi);
            if (erri) {
                outputErrors.push(erri);
            }
        });

        if (outputErrors.length) {
            if (flatten(inVals).length) {
                refErr(outputErrors, paths);
            }
            // This case is all-empty multivalued wildcard inputs,
            // which we would normally fire the callback for, except
            // some outputs are missing. So instead we treat it like
            // regular missing inputs and just silently prevent it.
            return {
                ...cb,
                executionPromise: null
            };
        }

        const __promise = new Promise<CallbackResult>(resolve => {
            let payload: any;
            try {
                payload = {
                    output,
                    outputs: isMultiOutputProp(output) ? outputs : outputs[0],
                    inputs: inVals,
                    changedPropIds: keys(cb.changedPropIds),
                };
                if (cb.callback.state.length) {
                    payload.state = fillVals(paths, layout, cb, state, 'State');
                }
            } catch (error) {
                resolve({ error });
            }

            function handleClientside(clientside_function: any, payload: any) {
                const dc = ((window as any).dash_clientside = (window as any).dash_clientside || {});
                if (!dc.no_update) {
                    Object.defineProperty(dc, 'no_update', {
                        value: { description: 'Return to prevent updating an Output.' },
                        writable: false,
                    });

                    Object.defineProperty(dc, 'PreventUpdate', {
                        value: { description: 'Throw to prevent updating all Outputs.' },
                        writable: false,
                    });
                }

                const { inputs, outputs, state } = payload;

                let returnValue;

                try {
                    const { namespace, function_name } = clientside_function;
                    let args = inputs.map(getVals);
                    if (state) {
                        args = concat(args, state.map(getVals));
                    }
                    returnValue = dc[namespace][function_name](...args);
                } catch (e) {
                    if (e === dc.PreventUpdate) {
                        return {};
                    }
                    throw e;
                }

                if (typeof returnValue?.then === 'function') {
                    throw new Error(
                        'The clientside function returned a Promise. ' +
                        'Promises are not supported in Dash clientside ' +
                        'right now, but may be in the future.'
                    );
                }

                const data: any = {};
                zipIfArray(outputs, returnValue).forEach(([outi, reti]) => {
                    zipIfArray(outi, reti).forEach(([outij, retij]) => {
                        const { id, property } = outij;
                        const idStr = stringifyId(id);
                        const dataForId = (data[idStr] = data[idStr] || {});
                        if (retij !== dc.no_update) {
                            dataForId[property] = retij;
                        }
                    });
                });
                return data;
            }

            function handleServerside(payload: any) {
                if (hooks.request_pre !== null) {
                    hooks.request_pre(payload);
                }

                return fetch(
                    `${urlBase(config)}_dash-update-component`,
                    mergeDeepRight(config.fetch, {
                        method: 'POST',
                        headers: getCSRFHeader(),
                        body: JSON.stringify(payload),
                    })
                ).then(res => {
                    const { status } = res;
                    if (status === STATUS.OK) {
                        return res.json().then(data => {
                            const { multi, response } = data;
                            if (hooks.request_post !== null) {
                                hooks.request_post(payload, response);
                            }

                            if (multi) {
                                return response;
                            }

                            const { output } = payload;
                            const id = output.substr(0, output.lastIndexOf('.'));
                            return { [id]: response.props };
                        });
                    }
                    if (status === STATUS.PREVENT_UPDATE) {
                        return {};
                    }
                    throw res;
                });
            }

            if (clientside_function) {
                try {
                    resolve({ data: handleClientside(clientside_function, payload) });
                } catch (error) {
                    resolve({ error });
                }
                return null;
            } else {
                handleServerside(payload)
                    .then(data => resolve({ data }))
                    .catch(error => resolve({ error }));
            }
        });

        const newCb = {
            ...cb,
            executionPromise: __promise
        };

        return newCb;
    } catch (error) {
        return {
            ...cb,
            executionPromise: { error }
        };
    }
}