import {assocPath, includes, pathOr} from 'ramda';

import {LoadingPayload} from '../actions/loading';

type LoadingState = {
    [k: string]: LoadingPayload[];
};

type LoadingAction = {
    type: 'LOADING' | 'LOADED';
    payload: LoadingPayload;
};

export default function loading(
    state: LoadingState = {},
    action: LoadingAction
) {
    switch (action.type) {
        case 'LOADED':
            return action.payload.reduce((acc, load) => {
                const loadPath = [JSON.stringify(load.path)];
                const prev = pathOr<any>([], loadPath, acc);
                return assocPath(
                    loadPath,
                    prev.filter(
                        (loading: any) => loading.property !== load.property
                    ),
                    acc
                );
            }, state);
        case 'LOADING':
            return action.payload.reduce((acc, load) => {
                const loadPath = [JSON.stringify(load.path)];
                const prev = pathOr<any>([], loadPath, acc);
                if (!includes(load, prev)) {
                    // duplicate outputs
                    prev.push(load);
                }
                return assocPath(loadPath, prev, acc);
            }, state);
        default:
            return state;
    }
}
