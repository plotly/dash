import {append, assocPath, includes, lensPath, mergeRight, view} from 'ramda';

import {getAction} from '../actions/constants';

const layout = (state = {}, action) => {
    if (action.type === getAction('SET_LAYOUT')) {
        return action.payload;
    } else if (
        includes(action.type, [
            'UNDO_PROP_CHANGE',
            'REDO_PROP_CHANGE',
            getAction('ON_PROP_CHANGE')
        ])
    ) {
        const propPath = append('props', action.payload.itempath);
        const existingProps = view(lensPath(propPath), state);
        const mergedProps = mergeRight(existingProps, action.payload.props);
        return assocPath(propPath, mergedProps, state);
    }

    return state;
};

export default layout;
