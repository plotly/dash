import {
    concat,
    difference,
    reduce
} from 'ramda';

export enum CallbackActionType {
    AddApplied = 'Callbacks.AddApplied',
    AddExecuted = 'Callbacks.AddExecuted',
    AddExecuting = 'Callbacks.AddExecuting',
    AddPrioritized = 'Callbacks.AddPrioritized',
    AddRequested = 'Callbacks.AddRequested',
    AddWatched = 'Callbacks.AddWatched',
    RemoveApplied = 'Callbacks.RemoveApplied',
    RemoveExecuted = 'Callbacks.RemoveExecuted',
    RemoveExecuting = 'Callbacks.RemoveExecuting',
    RemovePrioritized = 'Callbacks.ReomvePrioritized',
    RemoveRequested = 'Callbacks.RemoveRequested',
    RemoveWatched = 'Callbacks.RemoveWatched'
}

export enum CallbackAggregateActionType {
    AddCompleted = 'Callbacks.Completed',
    Aggregate = 'Callbacks.Aggregate'
}

type CallbackId = string | { [key: string]: any }

export interface ICallbackProperty {
    id: CallbackId;
    property: string;
}

export interface ICallback {
    anyVals: any[] | string;
    callback: {
        clientside_function: string;
        input: string;
        inputs: ICallbackProperty[];
        output: string;
        outputs: ICallbackProperty[];
        state: ICallbackProperty[];
    };
    getInputs: (paths: any) => ICallbackProperty[];
    getOutputs: (paths: any) => ICallbackProperty[];
    getState: (paths: any) => ICallbackProperty[];
    prevent_initial_call: boolean;

    [key: string]: any;
}

export interface IExecutingCallback extends ICallback {
    executionPromise: Promise<CallbackResult> | CallbackResult | null;
}

export interface IExecutedCallback extends IExecutingCallback {
    executionResult: CallbackResult | null;
}


export type CallbackResult = {
    data?: any;
    error?: Error
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
    completed: number;
}

const DEFAULT_STATE: ICallbacksState = {
    executed: [],
    executing: [],
    prioritized: [],
    requested: [],
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
    [CallbackActionType.AddWatched]: concat,
    [CallbackActionType.RemoveApplied]: difference,
    [CallbackActionType.RemoveExecuted]: difference,
    [CallbackActionType.RemoveExecuting]: difference,
    [CallbackActionType.RemovePrioritized]: difference,
    [CallbackActionType.RemoveRequested]: difference,
    [CallbackActionType.RemoveWatched]: difference,
};

const fields: {
    [key: string]: keyof Omit<ICallbacksState, 'completed'>
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