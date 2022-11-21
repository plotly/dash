import {
    concat,
    mergeDeepRight,
    mergeDeepWith,
    unionWith,
    eqBy,
    prop,
    dissocPath,
    path,
    propEq,
    findIndex
} from 'ramda';

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
    } else if (action.type === getAction('REMOVE_PATH')) {
        if (action.payload.objPath) {
            const index = findIndex(
                propEq('path', action.payload.objPath),
                path(action.payload.path, state)
            );
            return dissocPath(concat(action.payload.path, [index]), state);
        }
        return dissocPath(action.payload.path, state);
    }
    return state;
};

export default paths;
