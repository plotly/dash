import {includes, mergeRight, path} from 'ramda';

import {getAction} from '../actions/constants';

const layout = (state = {}, action) => {
    if (action.type === getAction('SET_LAYOUT')) {
        return {...action.payload};
    } else if (
        includes(action.type, [
            'UNDO_PROP_CHANGE',
            'REDO_PROP_CHANGE',
            getAction('ON_PROP_CHANGE')
        ])
    ) {
        const component = path(action.payload.itempath, state);
        component.props = mergeRight(component.props, action.payload.props);
    }

    return state;
};

export default layout;
