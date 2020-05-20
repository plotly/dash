import { ICallbacksState } from '../reducers/callbacks';

export const getPendingCallbacks = ({
    executed,
    executing,
    prioritized,
    requested,
    watched
}: ICallbacksState) => [
    ...requested,
    ...prioritized,
    ...executing,
    ...watched,
    ...executed
];