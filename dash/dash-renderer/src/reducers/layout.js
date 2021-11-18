import {append, assocPath, includes, lensPath, mergeRight, view} from 'ramda';

import {getAction} from '../actions/constants';
import {SERIALIZER_BOOKKEEPER, deserializeLayout} from '../serializers';

const layout = (state = {}, action) => {
    if (action.type === getAction('SET_LAYOUT')) {
        return deserializeLayout(action.payload);
    } else if (
        includes(action.type, [
            'UNDO_PROP_CHANGE',
            'REDO_PROP_CHANGE',
            getAction('ON_PROP_CHANGE')
        ])
    ) {
        const propPath = append('props', action.payload.itempath);
        const existingProps = view(lensPath(propPath), state);
        const mergedProps = mergeRight(existingProps, action.payload.props);
        let newState = state;

        if (action.payload.source === 'response') {
            newState = assocPath(
                append(SERIALIZER_BOOKKEEPER, action.payload.itempath),
                deserializeLayout({props: mergedProps})?.[
                    SERIALIZER_BOOKKEEPER
                ],
                newState
            );
        }

        return assocPath(propPath, mergedProps, newState);
    }

    return state;
};

export default layout;
