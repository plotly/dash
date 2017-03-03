import {crawlLayout, hasId} from './utils'
import R from 'ramda'

const initialPaths = {};


const paths = (state = initialPaths, action) => {
    switch (action.type) {
        case 'COMPUTE_PATHS': {
            const {subTree, startingPath} = action.payload;
            const newState = Object.assign({}, state);

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
