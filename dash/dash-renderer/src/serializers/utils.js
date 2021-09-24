import {type, has, prop} from 'ramda';

const PROP_TYPE = '__type';
const PROP_VALUE = '__value';
export const DASH_BOOK_KEEPER = '__dash_serialized_props';

/*
    What does this do?

    - Iterates over given `props` and see if any `props` value is serialized by Dash
    - For all `props` that is serialized by Dash, we create a bookkeeper record
        For the given `props` - {`propKey` = `propValue`} where `propValue` will be {__type: DataFrame, __value: any}
        - Bookkeeper record will look like {$propKey: $__type}, {data: 'DataFrame'} in our example
        - We'll create an array of all bookkeepers from this component - // I assume we will likely have more than one props to be serialized in a component.
        - Then save it to `extraProps`, which will look like
            extraProps: {
                ... other_extra_props,
                __dash_serialized_props: [
                    'data': 'DataFrame',        
                    ...
                ]
            }

    - Finally component will receive modified `props` (values stripped out) & `extraProps` which now contains bookkeepers
        input:
            props: {
                ... any normal primitive props,
                data: { __type: 'DataFrame', __value: whatever_we_dont_care_for_now }
            },
            extraProps: {}

        output: 
            props: {
                ... any normal primitive props,
                data: whatever_we_dont_care_for_now,        // this props now receive stripped out value
            },
            extraProps: {
                __dash_serialized_props: [
                    'data': 'DataFrame'                     // the `data` props were serialized by Dash and it's value type was 'DataFrame'
                ]
            }
    What does this do?

    - Iterates over given `props` and see if any `props` value is serialized by Dash
    - For all `props` that is serialized by Dash, we create a bookkeeper record
        For the given `props` - {`propKey` = `propValue`} where `propValue` will be {__type: DataFrame, __value: any}
        - Bookkeeper record will look like {$propKey: $__type}, {data: 'DataFrame'} in our example
        - We'll create an array of all bookkeepers from this component - // I assume we will likely have more than one props to be serialized in a component.
        - Then save it to `extraProps`, which will look like
            extraProps: {
                ... other_extra_props,
                __dash_serialized_props: [
                    'data': 'DataFrame',
                    ...
                ]
            }

    - Finally component will receive modified `props` (values stripped out) & `extraProps` which now contains bookkeepers
        input:
            props: {
                ... any normal primitive props,
                data: { __type: 'DataFrame', __value: whatever_we_dont_care_for_now }
            },
            extraProps: {}

        output:
            props: {
                ... any normal primitive props,
                data: whatever_we_dont_care_for_now,        // this props now receive stripped out value
            },
            extraProps: {
                __dash_serialized_props: [
                    'data': 'DataFrame'                     // the `data` props were serialized by Dash and it's value type was 'DataFrame'
                ]
            }

*/
export const deserializeProps = props => {
    const dashSerializedProps = [];
    const newProps = {};

    for (const [key, value] of Object.entries(props)) {
        if (isDashSerializedValue(value)) {
            const bookkeeper = {}; // this will look like {data: 'DataFrame'} meaning {$propName: $serializationType}
            bookkeeper[key] = stripDashSerializedType(value);
            dashSerializedProps.push(bookkeeper);
            newProps[key] = stripDashSerializedValue(value);
        } else {
            // just pass as it is
            newProps[key] = value;
        }
    }

    return {
        props: newProps,
        serializedKeys: dashSerializedProps
    };
};

export const isDashSerializedValue = object =>
    type(object) === 'Object' &&
    has(PROP_TYPE, object) &&
    has(PROP_VALUE, object);

const stripDashSerializedValue = obj => prop(PROP_VALUE, obj);
const stripDashSerializedType = obj => prop(PROP_TYPE, obj);

/*
    Whenever we process callbacks, we want to send serializedValue back to server, and this func will do that
*/
export const dashSerializeValue = (type, value) => {
    const serializedValue = {};
    serializedValue[PROP_TYPE] = type;
    serializedValue[PROP_VALUE] = value;
    return JSON.stringify(serializedValue);
};

/*
    To get `dashSerializeValue` func above working correctly, we need to know what was the `__type` for the given props before stripping out

    This func expects to receive `extraProps` where we stored bookkeeper, with propName to search for __type
*/
export const getOriginalSerializationType = (extraProps, propName) => {
    if (
        extraProps?.[DASH_BOOK_KEEPER] &&
        type(extraProps[DASH_BOOK_KEEPER]) === 'Array'
    ) {
        const dashSerializedProps = extraProps[DASH_BOOK_KEEPER];
        // find the bookkeeping record for the prop, { data: 'DataFrame' }
        const theProp = dashSerializedProps.find(bookkeeper =>
            has(propName, bookkeeper)
        );
        return theProp ? theProp[propName] : undefined;
    }

    return undefined;
};
