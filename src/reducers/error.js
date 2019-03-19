import {findIndex, propEq, remove} from 'ramda';

const initialError = {
    frontEnd: [],
    backEnd: {},
};

function error(state = initialError, action) {
    switch (action.type) {
        case 'ON_ERROR': {
            if (action.payload.type === 'frontEnd') {
                return {
                    frontEnd: [...state.frontEnd, action.payload],
                    backEnd: state.backEnd,
                };
            } else if (action.payload.type === 'backEnd') {
                return {
                    frontEnd: state.frontEnd,
                    backEnd: action.payload,
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
                return {
                    frontEnd: state.frontEnd,
                    backEnd: {},
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
