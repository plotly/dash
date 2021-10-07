import {type, prop} from 'ramda';

const PROP_TYPE = '__type';
const PROP_VALUE = '__value';
export const DASH_BOOK_KEEPER = '__dash_serialized_props';

export const createBookkeeper = layout => {
    const markedLayout = {...layout, [DASH_BOOK_KEEPER]: {}};
    const {
        props,
        props: {children}
    } = layout;
    if (type(children) === 'Array') {
        markedLayout.props.children = children.map(child =>
            createBookkeeper(child)
        );
    }

    if (type(children) === 'Object') {
        markedLayout.props.children = createBookkeeper(children);
    }

    Object.entries(props).forEach(([key, value]) => {
        if (prop(PROP_TYPE, value)) {
            markedLayout[DASH_BOOK_KEEPER][key] = prop(PROP_TYPE, value);
            markedLayout.props[key] = prop(PROP_VALUE, value);
        } else {
            markedLayout.props[key] = value;
        }
    });
    return markedLayout;
};

export const dashSerializeValue = (type, value) => {
    if (!type) return value;
    const serializedValue = {};
    serializedValue[PROP_TYPE] = type;
    serializedValue[PROP_VALUE] = value;
    return JSON.stringify(serializedValue);
};
