import {append, assocPath, contains, lensPath, merge, view} from 'ramda';

import {ACTIONS} from '../actions/constants';

const layout = (state = {}, action) => {
    if (action.type === ACTIONS('SET_LAYOUT')) {

        return action.payload;

    } else if (contains(
        action.type,
        ['UNDO_PROP_CHANGE', 'REDO_PROP_CHANGE', ACTIONS('ON_PROP_CHANGE')]
    )) {

        let propPath = append('props', action.payload.itempath);
        const existingProps = view(lensPath(propPath), state);
        const mergedProps = merge(existingProps, action.payload.props);
        state = assocPath(propPath, mergedProps, state);
        return state;

    } else {

        return state;

    }
}

export default layout;
