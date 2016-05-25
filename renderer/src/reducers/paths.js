import {crawlLayout, createTreePath} from './utils'

import spec from '../spec.js'; // TODO: this'll eventually load from the API

const initialPaths = {};

crawlLayout(spec, (child, itempath) => {
    if(child.props && child.props.id) {
        initialPaths[child.props.id] = createTreePath(itempath);
    }
});

const paths = (state = initialPaths, action) => {
    switch (action.type) {
        default:
            return state;
    }
}

export default paths;
