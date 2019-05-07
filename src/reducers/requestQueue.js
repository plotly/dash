import {clone} from 'ramda';

const requestQueue = (state = [], action) => {
    switch (action.type) {
        case 'SET_REQUEST_QUEUE':
            return clone(action.payload);

        default:
            return state;
    }
};

export default requestQueue;
