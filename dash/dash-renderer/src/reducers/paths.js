import {mergeDeepRight, mergeDeepWith, unionWith, eqBy, prop} from 'ramda';

import {getAction} from '../actions/constants';

const initialPaths = {strs: {}, objs: {}};

const paths = (state = initialPaths, action) => {
    if (action.type === getAction('ADD_PATH')) {
        if (action.payload.strs) {
            return mergeDeepRight(state, action.payload);
        }
        return mergeDeepWith(
            unionWith(eqBy(prop('path'))),
            state,
            action.payload
        );
    }
    return state;
};

export default paths;
