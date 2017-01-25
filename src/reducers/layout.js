import R from 'ramda';
import Immutable from 'immutable';

// TODO: this should be a prop of the high-level component
import {ACTIONS} from '../actions';
import {createTreePath} from './utils';

const layout = (state = Immutable.fromJS({}), action) => {
    switch (action.type) {

        case ACTIONS('SET_LAYOUT'):
            return action.payload;

        // Update the props of the component
        case ACTIONS('ON_PROP_CHANGE'): {
            let propPath = R.append('props', action.payload.itempath);
            state = state.mergeIn(propPath, action.payload.props);
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
