import {
    includes,
    mergeRight,
    append,
    view,
    lensPath,
    assocPath,
    dissocPath
} from 'ramda';

import {getAction} from '../actions/constants';

const layout = (state = {}, action) => {
    if (action.type === getAction('SET_LAYOUT')) {
        if (Array.isArray(action.payload)) {
            return [...action.payload];
        }
        return {...action.payload};
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
    // Custom component rendered out of tree.
    else if (action.type === getAction('INSERT_COMPONENT')) {
        const {component, componentPath} = action.payload;
        return assocPath(componentPath, component, state);
    } else if (action.type === getAction('REMOVE_COMPONENT')) {
        const {componentPath} = action.payload;
        return dissocPath(componentPath, state);
    }

    return state;
};

export default layout;
