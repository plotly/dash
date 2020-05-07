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
    AddPrioritized = 'Callbacks.AddPrioritized',
    AddRequested = 'Callbacks.AddRequested',
    AddWatched = 'Callbacks.Watched',
    RemoveExecuted = 'Callbacks.RemoveExecuted',
    RemoveExecuting = 'Callbacks.RemoveExecuting',
    RemovePrioritized = 'Callbacks.ReomvePrioritized',
    RemoveRequested = 'Callbacks.RemoveRequested',
    RemoveWatched = 'Callbacks.RemoveWatched'
}

export enum CallbackAggregateActionType {
    Aggregate = 'Callbacks.Aggregate'
}

export type CallbackResult = {
    data: any;
} | { error: any };

export type Callback = {
    executionResult?: Promise<CallbackResult> | CallbackResult | null;
    [key: string]: any;
};

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
    watched: Callback[];
}

const DEFAULT_STATE: ICallbacksState = {
    executed: [],
    executing: [],
    prioritized: [],
    requested: [],
    watched: []
};

const transforms: {
    [key: string]: (a1: Callback[], a2: Callback[]) => Callback[]
} = {
    [CallbackActionType.AddExecuted]: concat,
    [CallbackActionType.AddExecuting]: concat,
    [CallbackActionType.AddPrioritized]: concat,
    [CallbackActionType.AddRequested]: concat,
    [CallbackActionType.AddWatched]: concat,
    [CallbackActionType.RemoveExecuted]: difference,
    [CallbackActionType.RemoveExecuting]: difference,
    [CallbackActionType.RemovePrioritized]: difference,
    [CallbackActionType.RemoveRequested]: difference,
    [CallbackActionType.RemoveWatched]: difference,
};

const fields: {
    [key: string]: keyof ICallbacksState
} = {
    [CallbackActionType.AddExecuted]: 'executed',
    [CallbackActionType.AddExecuting]: 'executing',
    [CallbackActionType.AddPrioritized]: 'prioritized',
    [CallbackActionType.AddRequested]: 'requested',
    [CallbackActionType.AddWatched]: 'watched',
    [CallbackActionType.RemoveExecuted]: 'executed',
    [CallbackActionType.RemoveExecuting]: 'executing',
    [CallbackActionType.RemovePrioritized]: 'prioritized',
    [CallbackActionType.RemoveRequested]: 'requested',
    [CallbackActionType.RemoveWatched]: 'watched'
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