import {getAction} from '../actions/constants';

const initialPaths = {strs: {}, objs: {}};

const paths = (state = initialPaths, action) => {
    if (action.type === getAction('SET_PATHS')) {
        return action.payload;
    }
    return state;
};

export default paths;
