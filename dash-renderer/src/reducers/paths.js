import {crawlLayout, hasPropsId} from './utils';
import R from 'ramda';
import {getAction} from '../actions/constants';

const initialPaths = null;

const paths = (state = initialPaths, action) => {
    switch (action.type) {
        case getAction('COMPUTE_PATHS'): {
            const {subTree, startingPath} = action.payload;
            let oldState = state;
            if (R.isNil(state)) {
                oldState = {};
            }
            let newState;

            // if we're updating a subtree, clear out all of the existing items
            if (!R.isEmpty(startingPath)) {
                const removeKeys = R.filter(
                    k =>
                        R.equals(
                            startingPath,
                            R.slice(0, startingPath.length, oldState[k])
                        ),
                    R.keys(oldState)
                );
                newState = R.omit(removeKeys, oldState);
            } else {
                newState = R.merge({}, oldState);
            }

            crawlLayout(subTree, function assignPath(child, itempath) {
                if (hasPropsId(child)) {
                    newState[child.props.id] = R.concat(startingPath, itempath);
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
