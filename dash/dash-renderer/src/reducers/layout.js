import {append, assocPath, lensPath, mergeRight, view} from 'ramda';

import {getAction} from '../actions/constants';
import {SERIALIZER_BOOKKEEPER} from '../serializers';

const propChangeReducer = (state, action) => {
    const propPath = append('props', action.payload.itempath);
    const existingProps = view(lensPath(propPath), state);
    const mergedProps = mergeRight(existingProps, action.payload.props);
    let newState = state;

    if (action.payload.source === 'response') {
        newState = assocPath(
            append(SERIALIZER_BOOKKEEPER, action.payload.itempath),
            action.payload.deserializedLayout?.[SERIALIZER_BOOKKEEPER],
            newState
        );
    }

    return assocPath(propPath, mergedProps, newState);
};

const layout = (state = {}, action) => {
    switch (action.type) {
        case getAction('SET_LAYOUT'):
            return action.payload;
        case getAction('UNDO_PROP_CHANGE'):
        case getAction('REDO_PROP_CHANGE'):
        case getAction('ON_PROP_CHANGE'):
            return propChangeReducer(state, action);
        default:
            return state;
    }
};

export default layout;
