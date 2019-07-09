import {crawlLayout, hasPropsId} from './utils';
import {
    concat,
    equals,
    filter,
    isEmpty,
    isNil,
    keys,
    mergeRight,
    omit,
    slice,
} from 'ramda';
import {getAction} from '../actions/constants';

const initialPaths = null;

const paths = (state = initialPaths, action) => {
    switch (action.type) {
        case getAction('COMPUTE_PATHS'): {
            const {subTree, startingPath} = action.payload;
            let oldState = state;
            if (isNil(state)) {
                oldState = {};
            }
            let newState;

            // if we're updating a subtree, clear out all of the existing items
            if (!isEmpty(startingPath)) {
                const removeKeys = filter(
                    k =>
                        equals(
                            startingPath,
                            slice(0, startingPath.length, oldState[k])
                        ),
                    keys(oldState)
                );
                newState = omit(removeKeys, oldState);
            } else {
                newState = mergeRight({}, oldState);
            }

            crawlLayout(subTree, function assignPath(child, itempath) {
                if (hasPropsId(child)) {
                    newState[child.props.id] = concat(startingPath, itempath);
                }
            });

            return newState;
        }

        default: {
            return state;
        }
    }
};

export default paths;
