import {
    concat,
    difference,
    reduce
} from 'ramda';

import {
    ICallback,
    IExecutedCallback,
    IExecutingCallback,
    IStoredCallback
} from '../types/callbacks';

export enum CallbackActionType {
    AddApplied = 'Callbacks.AddApplied',
    AddExecuted = 'Callbacks.AddExecuted',
    AddExecuting = 'Callbacks.AddExecuting',
    AddPrioritized = 'Callbacks.AddPrioritized',
    AddRequested = 'Callbacks.AddRequested',
    AddStored = 'Callbacks.AddStored',
    AddWatched = 'Callbacks.AddWatched',
    RemoveApplied = 'Callbacks.RemoveApplied',
    RemoveExecuted = 'Callbacks.RemoveExecuted',
    RemoveExecuting = 'Callbacks.RemoveExecuting',
    RemovePrioritized = 'Callbacks.ReomvePrioritized',
    RemoveRequested = 'Callbacks.RemoveRequested',
    RemoveStored = 'Callbacks.RemoveStored',
    RemoveWatched = 'Callbacks.RemoveWatched'
}

export enum CallbackAggregateActionType {
    AddCompleted = 'Callbacks.Completed',
    Aggregate = 'Callbacks.Aggregate'
}

export interface IAggregateAction {
    type: CallbackAggregateActionType.Aggregate,
    payload: (ICallbackAction | ICompletedAction | null)[]
}

export interface ICallbackAction {
    type: CallbackActionType;
    payload: ICallback[];
}

export interface ICompletedAction {
    type: CallbackAggregateActionType.AddCompleted,
    payload: number
}

type CallbackAction =
    IAggregateAction |
    ICallbackAction |
    ICompletedAction;

export interface ICallbacksState {
    requested: ICallback[];
    prioritized: ICallback[];
    executing: IExecutingCallback[];
    watched: IExecutingCallback[];
    executed: IExecutedCallback[];
    stored: IStoredCallback[];
    completed: number;
}

const DEFAULT_STATE: ICallbacksState = {
    executed: [],
    executing: [],
    prioritized: [],
    requested: [],
    stored: [],
    watched: [],
    completed: 0
};

const transforms: {
    [key: string]: (a1: ICallback[], a2: ICallback[]) => ICallback[]
} = {
    [CallbackActionType.AddApplied]: concat,
    [CallbackActionType.AddExecuted]: concat,
    [CallbackActionType.AddExecuting]: concat,
    [CallbackActionType.AddPrioritized]: concat,
    [CallbackActionType.AddRequested]: concat,
    [CallbackActionType.AddStored]: concat,
    [CallbackActionType.AddWatched]: concat,
    [CallbackActionType.RemoveApplied]: difference,
    [CallbackActionType.RemoveExecuted]: difference,
    [CallbackActionType.RemoveExecuting]: difference,
    [CallbackActionType.RemovePrioritized]: difference,
    [CallbackActionType.RemoveRequested]: difference,
    [CallbackActionType.RemoveStored]: difference,
    [CallbackActionType.RemoveWatched]: difference,
};

const fields: {
    [key: string]: keyof Omit<ICallbacksState, 'completed'>
} = {
    [CallbackActionType.AddExecuted]: 'executed',
    [CallbackActionType.AddExecuting]: 'executing',
    [CallbackActionType.AddPrioritized]: 'prioritized',
    [CallbackActionType.AddRequested]: 'requested',
    [CallbackActionType.AddStored]: 'stored',
    [CallbackActionType.AddWatched]: 'watched',
    [CallbackActionType.RemoveExecuted]: 'executed',
    [CallbackActionType.RemoveExecuting]: 'executing',
    [CallbackActionType.RemovePrioritized]: 'prioritized',
    [CallbackActionType.RemoveRequested]: 'requested',
    [CallbackActionType.RemoveStored]: 'stored',
    [CallbackActionType.RemoveWatched]: 'watched'
}

const mutateCompleted = (
    state: ICallbacksState,
    action: ICompletedAction
) => ({ ...state, completed: state.completed + action.payload });

const mutateCallbacks = (
    state: ICallbacksState,
    action: ICallbackAction
) => {
    const transform = transforms[action.type];
    const field = fields[action.type];

    return (!transform || !field || action.payload.length === 0) ?
        state : {
            ...state,
            [field]: transform(state[field], action.payload)
        };
}



export default (
    state: ICallbacksState = DEFAULT_STATE,
    action: CallbackAction
) => reduce((s, a) => {
    if (a === null) {
        return s;
    } else if (a.type === CallbackAggregateActionType.AddCompleted) {
        return mutateCompleted(s, a);
    } else {
        return mutateCallbacks(s, a);
    }
}, state, action.type === CallbackAggregateActionType.Aggregate ?
    action.payload :
    [action]
);