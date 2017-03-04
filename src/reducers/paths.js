import {crawlLayout, hasId} from './utils'
import R from 'ramda'

const initialPaths = {};


const paths = (state = initialPaths, action) => {
    switch (action.type) {
        case 'COMPUTE_PATHS': {
            const {subTree, startingPath} = action.payload;

            let newState;

            // if we're updating a subtree, clear out all of the existing items
            if (!R.isEmpty(startingPath)) {
                const removeKeys = R.filter(k => (
                    R.equals(startingPath, R.slice(0, startingPath.length, state[k]))
                ), R.keys(state));
                newState = R.omit(removeKeys, state);
            } else {
                newState = Object.assign({}, state);
            }

            crawlLayout(subTree, function assignPath(child, itempath) {
                if(hasId(child)) {

                    newState[child.props.id] = R.concat(startingPath, itempath);

                }
            });

            return newState;
        }

        default: {
            return state;
        }
    }
}

export default paths;
