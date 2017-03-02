import {crawlLayout} from './utils'
import R from 'ramda'

const initialPaths = {};

const paths = (state = initialPaths, action) => {
    switch (action.type) {
        case 'COMPUTE_PATHS': {
            const layout = action.payload;
            const newState = Object.assign({}, state);

            crawlLayout(layout, function assignPath(child, itempath) {
                if(R.type(child) === 'Object' &&
                   R.has('props', child) &&
                   R.has('id', child.props)
                ) {

                    newState[child.props.id] = itempath;

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
