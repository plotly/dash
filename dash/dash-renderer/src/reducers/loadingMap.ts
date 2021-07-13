export enum LoadingMapActionType {
    Set = 'LoadingMap.Set'
}

export interface ILoadingMapAction {
    type: LoadingMapActionType.Set;
    payload: any;
}

type LoadingMapState = any;
export {LoadingMapState};

const DEFAULT_STATE: LoadingMapState = {};

export default (
    state: LoadingMapState = DEFAULT_STATE,
    action: ILoadingMapAction
) => (action.type === LoadingMapActionType.Set ? action.payload : state);
