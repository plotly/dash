import {mergeRight} from 'ramda';

const initialError = {
    frontEnd: [],
    backEnd: [],
    backEndConnected: true
};

export default function error(state = initialError, action) {
    switch (action.type) {
        case 'ON_ERROR': {
            const {frontEnd, backEnd, backEndConnected} = state;
            // log errors to the console for stack tracing and so they're
            // available even with debugging off
            /* eslint-disable-next-line no-console */
            console.error(action.payload.error);

            if (action.payload.type === 'frontEnd') {
                return {
                    frontEnd: [
                        mergeRight(action.payload, {timestamp: new Date()}),
                        ...frontEnd
                    ],
                    backEnd,
                    backEndConnected
                };
            } else if (action.payload.type === 'backEnd') {
                return {
                    frontEnd,
                    backEnd: [
                        mergeRight(action.payload, {timestamp: new Date()}),
                        ...backEnd
                    ],
                    backEndConnected
                };
            }
            return state;
        }
        case 'SET_CONNECTION_STATUS': {
            return mergeRight(state, {backEndConnected: action.payload});
        }

        default: {
            return state;
        }
    }
}
