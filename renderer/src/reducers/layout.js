import R from 'ramda';
import Immutable from 'immutable';

import spec from '../spec.js';
import {ACTIONS} from '../actions';

const pad = R.curry((array, paddingValue) => array.reduce((r, v) => {
    r.push(paddingValue);
    r.push(v);
}));
const createTreePath = (array) => pad(array);

const layout = (state, action) => {
    switch (action.type) {
        case 'EDIT_CHILDREN_STRING':
            // TODO: Update the children component of the state with this action
            console.warn('EDIT_CHILDREN_STRING: ', action);

        // Update the props of the component
        case ACTIONS('ON_PROP_CHANGE'): {
            const path = createTreePath(action.payload.itempath);
            path.push('props');
            state = state.mergeIn(path, action.payload.props);
            return state;
        }
        case 'REORDER_CHILDREN': {
            // TODO: wire this in to our drop targets
            const itemTreePath = createTreePath(action.itempath);  // [3, 1, 4, 5]

            const targetTreePath = R.append(
                'children',
                createTreePath(action.targetpath)
            );

            const item = state.getIn(itemTreePath);
            state = state.deleteIn(itemTreePath);
            state = state.setIn(targetTreePath, item);
            return state;
        }
        default:
            return state;

    }
}

export default layout;
