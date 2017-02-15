import {append, assocPath, lensPath, merge, view} from 'ramda';

// TODO: this should be a prop of the high-level component
import {ACTIONS} from '../actions';

const layout = (state = {}, action) => {
    switch (action.type) {

        case ACTIONS('SET_LAYOUT'):
            return action.payload;

        // Update the props of the component
        case ACTIONS('ON_PROP_CHANGE'): {
            let propPath = append('props', action.payload.itempath);
            const existingProps = view(lensPath(propPath), state);
            const mergedProps = merge(existingProps, action.payload.props);
            state = assocPath(propPath, mergedProps, state);
            return state;
        }

        default:
            return state;

    }
}

export default layout;
