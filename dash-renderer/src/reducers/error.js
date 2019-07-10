import {findIndex, mergeRight, propEq, remove} from 'ramda';

const initialError = {
    frontEnd: [],
    backEnd: [],
};

function error(state = initialError, action) {
    switch (action.type) {
        case 'ON_ERROR': {
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

        case 'RESOLVE_ERROR': {
            if (action.payload.type === 'frontEnd') {
                const removeIdx = findIndex(
                    propEq('myUID', action.payload.myUID)
                )(state.frontEnd);
                return {
                    frontEnd: remove(removeIdx, 1, state.frontEnd),
                    backEnd: state.backEnd,
                };
            } else if (action.payload.type === 'backEnd') {
                const removeIdx = findIndex(
                    propEq('myUID', action.payload.myUID)
                )(state.backEnd);
                return {
                    frontEnd: state.frontEnd,
                    backEnd: remove(removeIdx, 1, state.backEnd),
                };
            }
            return state;
        }

        default: {
            return state;
        }
    }
}

export default error;
