import {type, has, prop} from 'ramda';

const PROP_TYPE = '__type';
const PROP_VALUE = '__value';
const DASH_BOOK_KEEPER = '__dash_serialized_props';

export const deserializeProps = (props, extraProps) => {
    const dashSerializedProps = [];
    const newProps = {};
    const newExtraProps = Object.assign({}, extraProps);

    for (const [key, value] of Object.entries(props)) {
        if (isDashSerializedValue(value)) {
            const bookkeeper = {};      // this will look like {data: 'DataFrame'} meaning {$propName: $serializationType}
            bookkeeper[key] = stripDashSerializedType(value);
            dashSerializedProps.push(bookkeeper);
            newProps[key] = stripDashSerializedValue(value);
        } else {
            // just pass as it is
            newProps[key] = value;
        }
    }

    newExtraProps[DASH_BOOK_KEEPER] = dashSerializedProps;
    return {props: newProps, extraProps: newExtraProps};
};

const isDashSerializedValue = object =>
    type(object) === 'Object' &&
    has(PROP_TYPE, object) &&
    has(PROP_VALUE, object);

const stripDashSerializedValue = obj => prop(PROP_VALUE, obj);
const stripDashSerializedType = obj => prop(PROP_TYPE, obj);

export const dashSerializeValue = (type, value) => {
    const serializedValue = {};
    serializedValue[PROP_TYPE] = type;
    serializedValue[PROP_VALUE] = value;
    return serializedValue;
}

export const getOriginalSerializationType = (extraProps, propName) => {
    if (extraProps?.[DASH_BOOK_KEEPER] && type(extraProps[DASH_BOOK_KEEPER]) === 'Array') {
        const dashSerializedProps = extraProps[DASH_BOOK_KEEPER];
        // find the bookkeeping record for the prop, { data: 'DataFrame' }
        const theProp = dashSerializedProps.find(bookkeeper => has(propName, bookkeeper));
        return theProp ? theProp[propName] : undefined;
    }

    return undefined;
}