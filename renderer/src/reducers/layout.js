import R from 'ramda';
import Immutable from 'immutable';

// TODO: this should be a prop of the high-level component
import spec from '../spec.js'; // do we need this now?
import {ACTIONS} from '../actions';

const pad = R.curry((array, paddingValue) => array.reduce((r, v) => {
    r.push(paddingValue);
    r.push(v);
    return r;
}, []));
const createTreePath = (array) => pad(array, 'children');

const layout = (state = Immutable.fromJS(spec), action) => {
    switch (action.type) {

        // Update the props of the component
        case ACTIONS('ON_PROP_CHANGE'): {
            const path = createTreePath(action.payload.itempath);
            path.push('props');
            state = state.mergeIn(path, action.payload.props);
            return state;
        }

        // TODO: this doesn't actually do anything yet
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
