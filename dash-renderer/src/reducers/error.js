import {mergeRight} from 'ramda';

const initialError = {
    frontEnd: [],
    backEnd: [],
};

export default function error(state = initialError, action) {
    switch (action.type) {
        case 'ON_ERROR': {
            // log errors to the console for stack tracing and so they're
            // available even with debugging off
            /* eslint-disable-next-line no-console */
            console.error(action.payload.error);

            if (action.payload.type === 'frontEnd') {
                return {
                    frontEnd: [
                        mergeRight(action.payload, {timestamp: new Date()}),
                        ...state.frontEnd,
                    ],
                    backEnd: state.backEnd,
                };
            } else if (action.payload.type === 'backEnd') {
                return {
                    frontEnd: state.frontEnd,
                    backEnd: [
                        mergeRight(action.payload, {timestamp: new Date()}),
                        ...state.backEnd,
                    ],
                };
            }
            return state;
        }

        default: {
            return state;
        }
    }
}
