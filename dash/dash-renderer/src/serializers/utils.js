import {type, has, prop} from 'ramda';

const PROP_TYPE = '__type';
const PROP_VALUE = '__value';
const DASH_KEYS = '__dash_serialized_keys';

export const deserializeProps = (props, extraProps) => {
    const dashSerializedKeys = [];
    const newProps = {};
    const newExtraProps = Object.assign({}, extraProps);

    for (const [key, value] of Object.entries(props)) {
        if (isDashSerializedValue(value)) {
            /* 
                book-keep `key` some where (`extraProps`) 
                so that we can grab it again when sending values to server again 
            */
            dashSerializedKeys.push(key);
            newProps[key] = stripDashSerializedValue(value);
        } else {
            // just pass as it is
            newProps[key] = value;
        }
    }

    newExtraProps[DASH_KEYS] = dashSerializedKeys;
    return {props: newProps, extraProps: newExtraProps};
};

const isDashSerializedValue = object =>
    type(object) === 'Object' &&
    has(PROP_TYPE, object) &&
    has(PROP_VALUE, object);

const stripDashSerializedValue = value => prop(PROP_VALUE, value);
