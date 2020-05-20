type CallbackId = string | { [key: string]: any }

export interface ICallbackProperty {
    id: CallbackId;
    property: string;
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
    executionGroup?: string;
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

export interface IStoredCallback extends IExecutedCallback {
    executionMeta: {
        allProps: string[];
        updatedProps: string[];
    }
}

interface ICallbackPayload {
    changedPropIds: any[];
    inputs: any[];
    output: string;
    outputs: any[];
}

export type CallbackResult = {
    data?: any;
    error?: Error;
    payload: ICallbackPayload | null;
}