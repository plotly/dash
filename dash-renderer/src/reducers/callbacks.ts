import {
    concat,
    difference,
    reduce
} from 'ramda';

/**
 * Callback states and transitions
 *
 * State                transition --> {State}
 * -------------------------------
 * {Requested}          prioritize --> {Prioritized}
 * {Prioritized}        execute --> {Executing}
 * {Executing}          processResult --> {Executed}
 * {Executed}           (none)
 */

export enum CallbackActionType {
    AddExecuted = 'Callbacks.AddExecuted',
    AddExecuting = 'Callbacks.AddExecuting',
    AddRequested = 'Callbacks.AddRequested',
    AddPrioritized = 'Callbacks.AddPrioritized',
    RemoveExecuted = 'Callbacks.RemoveExecuted',
    RemoveExecuting = 'Callbacks.RemoveExecuting',
    RemoveRequested = 'Callbacks.RemoveRequested',
    RemovePrioritized = 'Callbacks.ReomvePrioritized',
}

export enum CallbackAggregateActionType {
    Aggregate = 'Callbacks.Aggregate'
}

export type Callback = any;

interface ICallbackAction {
    type: CallbackActionType | CallbackAggregateActionType | string;
    payload: Callback[];
}

type CallbackAction = ICallbackAction | {
    type: CallbackAggregateActionType.Aggregate,
    payload: ICallbackAction[]
};


export interface ICallbacksState {
    executed: Callback[];
    executing: Callback[];
    prioritized: Callback[];
    requested: Callback[];
}

const DEFAULT_STATE = {
    executed: [],
    executing: [],
    prioritized: [],
    requested: []
};

const transforms: {
    [key: string]: (a1: Callback[], a2: Callback[]) => Callback[]
} = {
    [CallbackActionType.AddExecuted]: concat,
    [CallbackActionType.AddExecuting]: concat,
    [CallbackActionType.AddPrioritized]: concat,
    [CallbackActionType.AddRequested]: concat,
    [CallbackActionType.RemoveExecuted]: difference,
    [CallbackActionType.RemoveExecuting]: difference,
    [CallbackActionType.RemovePrioritized]: difference,
    [CallbackActionType.RemoveRequested]: difference,
};

const fields: {
    [key: string]: keyof ICallbacksState
} = {
    [CallbackActionType.AddExecuted]: 'executed',
    [CallbackActionType.AddExecuting]: 'executing',
    [CallbackActionType.AddPrioritized]: 'prioritized',
    [CallbackActionType.AddRequested]: 'requested',
    [CallbackActionType.RemoveExecuted]: 'executed',
    [CallbackActionType.RemoveExecuting]: 'executing',
    [CallbackActionType.RemovePrioritized]: 'prioritized',
    [CallbackActionType.RemoveRequested]: 'requested',
}

export default (
    state: ICallbacksState = DEFAULT_STATE,
    action: CallbackAction
) => reduce((s, a) => {
    const transform = transforms[a.type];
    const field = fields[a.type];

    return (!transform || !field || a.payload.length === 0) ? s : {
        ...s,
        [field]: transform(s[field], a.payload)
    };
}, state, action.type === CallbackAggregateActionType.Aggregate ?
    action.payload :
    [action]
);