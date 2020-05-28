type CallbackId = string | { [key: string]: any }

export interface ICallbackDefinition {
    clientside_function?: {
        namespace: string;
        function_name: string;
    };
    input: string;
    inputs: ICallbackProperty[];
    output: string;
    outputs: ICallbackProperty[];
    prevent_initial_call: boolean;
    state: ICallbackProperty[];
}

export interface ICallbackProperty {
    id: CallbackId;
    property: string;
}

export interface ILayoutCallbackProperty extends ICallbackProperty {
    path: (string | number)[];
}

export interface ICallbackTemplate {
    anyVals: any[] | string;
    callback: ICallbackDefinition;
    changedPropIds: any;
    executionGroup?: string;
    initialCall: boolean;
    getInputs: (paths: any) => ILayoutCallbackProperty[][];
    getOutputs: (paths: any) => ILayoutCallbackProperty[][];
    getState: (paths: any) => ILayoutCallbackProperty[][];
    requestedOutputs: { [key: string]: any };
    resolvedId: any;
}

export interface ICallback extends ICallbackTemplate {
    priority: number[];
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