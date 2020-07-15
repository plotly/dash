export enum DependencyGraphActionType {
    Set = 'DependencyGraph.Set'
}

export interface IDependencyGraphAction {
    type: DependencyGraphActionType.Set;
    payload: any
}

export default (
    state: any = {},
    action: IDependencyGraphAction
) => action.type === DependencyGraphActionType.Set ?
        Boolean(console.log(action.payload)) || action.payload :
        state;
