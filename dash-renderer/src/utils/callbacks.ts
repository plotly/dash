import { ICallbacksState } from '../reducers/callbacks';

export const getPendingCallbacks = ({
    executed,
    executing,
    blocked,
    prioritized,
    requested,
    watched
}: ICallbacksState) => [
    ...requested,
    ...prioritized,
    ...blocked,
    ...executing,
    ...watched,
    ...executed
];
