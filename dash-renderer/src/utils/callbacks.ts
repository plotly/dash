import {omit, values} from 'ramda';

import {ICallbacksState} from '../reducers/callbacks';
import {ICallback} from '../types/callbacks';

export const getPendingCallbacks = (state: ICallbacksState) =>
    Array<ICallback>().concat(...values(omit(['stored', 'completed'], state)));
