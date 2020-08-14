export enum IsLoadingActionType {
    Set = 'IsLoading.Set'
}

export interface ILoadingMapAction {
    type: IsLoadingActionType.Set;
    payload: any;
}

type IsLoadingState = boolean;
export {IsLoadingState};

const DEFAULT_STATE: IsLoadingState = true;

export default (
    state: IsLoadingState = DEFAULT_STATE,
    action: ILoadingMapAction
) => (action.type === IsLoadingActionType.Set ? action.payload : state);
