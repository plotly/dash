import R from 'ramda';

import spec from '../spec.js';

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
            return state;
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
            return spec;
    }
}

export default layout;
