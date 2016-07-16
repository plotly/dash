import {crawlLayout, createTreePath} from './utils'

const initialPaths = {};

const paths = (state = initialPaths, action) => {
    switch (action.type) {
        case 'COMPUTE_PATHS': {
            const layout = action.payload;
            const newState = Object.assign({}, state);

            crawlLayout(layout, (child, itempath) => {
                if(child.props && child.props.id) {
                    newState[child.props.id] = createTreePath(itempath);
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
