import {
    append,
    assocPath,
    includes,
    lensPath,
    mergeRight,
    view,
    type
} from 'ramda';

import {getAction} from '../actions/constants';

const processProperties = node => {
    const updatedNode = {...node, propertyTypes: {}};
    const {
        props,
        props: {children}
    } = node;

    if (type(children) === 'Array') {
        updatedNode.props.children = children.map(child =>
            processProperties(child)
        );
    } else if (type(children) === 'Object' && !children.__type) {
        updatedNode.props.children = processProperties(children);
    }

    Object.entries(props).forEach(([key, value]) => {
        updatedNode.props[key] = value?.__value || value;
        updatedNode.propertyTypes[key] = value?.__type || null;
    });

    return updatedNode;
};

const layout = (state = {}, action) => {
    if (action.type === getAction('SET_LAYOUT')) {
        const updatedState = processProperties(action.payload);

        return updatedState;
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

        let updatedState = assocPath(propPath, mergedProps, state);
        if (action.payload.source === 'response') {
            updatedState = processProperties(updatedState);
        }

        return updatedState;
    }

    return state;
};

export default layout;
