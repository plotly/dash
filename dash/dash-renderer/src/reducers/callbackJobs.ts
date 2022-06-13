import {assoc, dissoc} from 'ramda';
import {ICallbackProperty} from '../types/callbacks';

type CallbackJobState = {[k: string]: CallbackJobPayload};

export type CallbackJobPayload = {
    cancelInputs?: ICallbackProperty[];
    cacheKey: string;
    jobId: string;
    progressDefault?: any;
};

type CallbackJobAction = {
    type: 'ADD_CALLBACK_JOB' | 'REMOVE_CALLBACK_JOB';
    payload: CallbackJobPayload;
};

const setJob = (job: CallbackJobPayload, state: CallbackJobState) =>
    assoc(job.jobId, job, state);
const removeJob = (jobId: string, state: CallbackJobState) =>
    dissoc(jobId, state);

export default function (
    state: CallbackJobState = {},
    action: CallbackJobAction
) {
    switch (action.type) {
        case 'ADD_CALLBACK_JOB':
            return setJob(action.payload, state);
        case 'REMOVE_CALLBACK_JOB':
            return removeJob(action.payload.jobId, state);
        default:
            return state;
    }
}
