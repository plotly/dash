import {concat, difference, reduce} from 'ramda';

import {
    ICallback,
    IExecutedCallback,
    IExecutingCallback,
    IStoredCallback,
    IPrioritizedCallback,
    IBlockedCallback,
    IWatchedCallback
} from '../types/callbacks';

export enum CallbackActionType {
    AddBlocked = 'Callbacks.AddBlocked',
    AddExecuted = 'Callbacks.AddExecuted',
    AddExecuting = 'Callbacks.AddExecuting',
    AddPrioritized = 'Callbacks.AddPrioritized',
    AddRequested = 'Callbacks.AddRequested',
    AddStored = 'Callbacks.AddStored',
    AddWatched = 'Callbacks.AddWatched',
    RemoveBlocked = 'Callbacks.RemoveBlocked',
    RemoveExecuted = 'Callbacks.RemoveExecuted',
    RemoveExecuting = 'Callbacks.RemoveExecuting',
    RemovePrioritized = 'Callbacks.RemovePrioritized',
    RemoveRequested = 'Callbacks.RemoveRequested',
    RemoveStored = 'Callbacks.RemoveStored',
    RemoveWatched = 'Callbacks.RemoveWatched'
}

export enum CallbackAggregateActionType {
    AddCompleted = 'Callbacks.Completed',
    Aggregate = 'Callbacks.Aggregate'
}

export interface IAggregateAction {
    type: CallbackAggregateActionType.Aggregate;
    payload: (ICallbackAction | ICompletedAction | null)[];
}

export interface ICallbackAction {
    type: CallbackActionType;
    payload: ICallback[];
}

export interface ICompletedAction {
    type: CallbackAggregateActionType.AddCompleted;
    payload: number;
}

type CallbackAction = IAggregateAction | ICallbackAction | ICompletedAction;

export interface ICallbacksState {
    requested: ICallback[];
    prioritized: IPrioritizedCallback[];
    blocked: IBlockedCallback[];
    executing: IExecutingCallback[];
    watched: IWatchedCallback[];
    executed: IExecutedCallback[];
    stored: IStoredCallback[];
    completed: number;
}

const DEFAULT_STATE: ICallbacksState = {
    blocked: [],
    executed: [],
    executing: [],
    prioritized: [],
    requested: [],
    stored: [],
    watched: [],
    completed: 0
};

const transforms: {
    [key: string]: (a1: ICallback[], a2: ICallback[]) => ICallback[];
} = {
    [CallbackActionType.AddBlocked]: concat,
    [CallbackActionType.AddExecuted]: concat,
    [CallbackActionType.AddExecuting]: concat,
    [CallbackActionType.AddPrioritized]: concat,
    [CallbackActionType.AddRequested]: concat,
    [CallbackActionType.AddStored]: concat,
    [CallbackActionType.AddWatched]: concat,
    [CallbackActionType.RemoveBlocked]: difference,
    [CallbackActionType.RemoveExecuted]: difference,
    [CallbackActionType.RemoveExecuting]: difference,
    [CallbackActionType.RemovePrioritized]: difference,
    [CallbackActionType.RemoveRequested]: difference,
    [CallbackActionType.RemoveStored]: difference,
    [CallbackActionType.RemoveWatched]: difference
};

const fields: {
    [key: string]: keyof Omit<ICallbacksState, 'completed'>;
} = {
    [CallbackActionType.AddBlocked]: 'blocked',
    [CallbackActionType.AddExecuted]: 'executed',
    [CallbackActionType.AddExecuting]: 'executing',
    [CallbackActionType.AddPrioritized]: 'prioritized',
    [CallbackActionType.AddRequested]: 'requested',
    [CallbackActionType.AddStored]: 'stored',
    [CallbackActionType.AddWatched]: 'watched',
    [CallbackActionType.RemoveBlocked]: 'blocked',
    [CallbackActionType.RemoveExecuted]: 'executed',
    [CallbackActionType.RemoveExecuting]: 'executing',
    [CallbackActionType.RemovePrioritized]: 'prioritized',
    [CallbackActionType.RemoveRequested]: 'requested',
    [CallbackActionType.RemoveStored]: 'stored',
    [CallbackActionType.RemoveWatched]: 'watched'
};

const mutateCompleted = (state: ICallbacksState, action: ICompletedAction) => ({
    ...state,
    completed: state.completed + action.payload
});

const mutateCallbacks = (state: ICallbacksState, action: ICallbackAction) => {
    const transform = transforms[action.type];
    const field = fields[action.type];

    return !transform || !field || action.payload.length === 0
        ? state
        : {
              ...state,
              [field]: transform(state[field], action.payload)
          };
};

export default (
    state: ICallbacksState = DEFAULT_STATE,
    action: CallbackAction
) =>
    reduce(
        (s, a) => {
            if (a === null) {
                return s;
            } else if (a.type === CallbackAggregateActionType.AddCompleted) {
                return mutateCompleted(s, a);
            }

            return mutateCallbacks(s, a);
        },
        state,
        action.type === CallbackAggregateActionType.Aggregate
            ? action.payload
            : [action]
    );
