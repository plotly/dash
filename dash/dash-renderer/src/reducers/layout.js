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
    }
    Object.entries(props).forEach(([key, value]) => {
        updatedNode.props[key] = value?.__value || value;
        updatedNode.propertyTypes[key] = value?.__type || null;
    });

    return updatedNode;
};

const layout = (state = {}, action) => {
    if (action.type === getAction('SET_LAYOUT')) {
        return processProperties(action.payload);
    } else if (
        includes(action.type, [
            'UNDO_PROP_CHANGE',
            'REDO_PROP_CHANGE',
            getAction('ON_PROP_CHANGE')
        ])
    ) {
        const propPath = append('props', action.payload.itempath);
        const propertyTypesPath = append(
            'propertyTypes',
            action.payload.itempath
        );

        const existingProps = view(lensPath(propPath), state);
        const mergedProps = mergeRight(existingProps, action.payload.props);

        const propertyValues = Object.entries(mergedProps).reduce(
            (a, [key, value]) => {
                return {...a, [key]: value.__value || value};
            },
            {}
        );

        const propertyTypes = Object.entries(mergedProps).reduce(
            (a, [key, value]) => {
                return {...a, [key]: value.__type || null};
            },
            {}
        );

        let updatedState = assocPath(propPath, propertyValues, state);
        if (action.payload.source === 'response') {
            updatedState = assocPath(
                propertyTypesPath,
                propertyTypes,
                updatedState
            );
        }

        return updatedState;
    }

    return state;
};

export default layout;
