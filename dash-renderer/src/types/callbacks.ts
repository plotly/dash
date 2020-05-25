type CallbackId = string | { [key: string]: any }

export interface ICallbackProperty {
    id: CallbackId;
    property: string;
}

export interface ILayoutCallbackProperty extends ICallbackProperty {
    path: (string | number)[];
}

export interface ICallback {
    anyVals: any[] | string;
    callback: {
        clientside_function?: {
            namespace: string;
            function_name: string;
        };
        input: string;
        inputs: ICallbackProperty[];
        output: string;
        outputs: ICallbackProperty[];
        state: ICallbackProperty[];
    };
    changedPropIds: any;
    executionGroup?: string;
    priority: number[];
    getInputs: (paths: any) => ILayoutCallbackProperty[];
    getOutputs: (paths: any) => ILayoutCallbackProperty[];
    getState: (paths: any) => ILayoutCallbackProperty[];
    prevent_initial_call: boolean;
    requestedOutputs: object;
    resolvedId: any;
}

export interface IExecutingCallback extends ICallback {
    executionPromise: Promise<CallbackResult> | CallbackResult | null;
}

export interface IExecutedCallback extends IExecutingCallback {
    executionResult: CallbackResult | null;
}

export interface IStoredCallback extends IExecutedCallback {
    executionMeta: {
        allProps: string[];
        updatedProps: string[];
    }
}

export interface ICallbackPayload {
    changedPropIds: any[];
    inputs: any[];
    output: string;
    outputs: any[];
    state?: any[] | null;
}

export type CallbackResult = {
    data?: any;
    error?: Error;
    payload: ICallbackPayload | null;
}