import {type, prop} from 'ramda';
import DataFrameSerializer from './pd.dataframe';

const PROP_TYPE = '__type';
const PROP_VALUE = '__value';
const PROP_ENGINE = '__engine';
const supportedTypes = {
    'pd.DataFrame': DataFrameSerializer
};

export const SERIALIZER_BOOKKEEPER = '__dash_serialized_props';
export const deserializeCbResponse = response => {
    if (Object.keys(response).length == 1) {
        return {
            [Object.keys(response)[0]]: deserializeLayout({
                props: Object.values(response)[0]
            }).props
        };
    } else {
        return deserializeLayout({props: response}).props;
    }
};

export const deserializeLayout = layout => {
    const markedLayout = {...layout, [SERIALIZER_BOOKKEEPER]: {}};
    const {
        props,
        props: {children}
    } = layout;
    if (type(children) === 'Array')
        for (let index = 0; index < children.length; index++) {
            children[index] = deserializeLayout(children[index]);
        }

    if (type(children) === 'Object')
        markedLayout.props.children = deserializeLayout(children);

    for (const [key, value] of Object.entries(props)) {
        if (prop(PROP_TYPE, value)) {
            await deserializeValue(markedLayout, key, value);
        } else {
            markedLayout.props[key] = value;
        }
    }
    return markedLayout;
};

const deserializeValue = (
    layout,
    key,
    {[PROP_TYPE]: type, [PROP_ENGINE]: engine, [PROP_VALUE]: originalValue}
) => {
    const [val, missingProps] = (await supportedTypes[type]?.deserialize(
        engine,
        originalValue
    )) || [originalValue, {}];
    layout[SERIALIZER_BOOKKEEPER][key] = {
        type,
        engine,
        autoFilledProps: Object.keys(missingProps)
    };
    layout.props[key] = val;
    for (const k in missingProps) {
        layout.props[k] = missingProps[k];
    }
};

export const serializeValue = (
    {type, engine, autoFilledProps},
    value,
    props
) => {
    if (!type) return value;
    const serializedValue = {};
    serializedValue[PROP_TYPE] = type;
    serializedValue[PROP_ENGINE] = engine;
    const additionalProps = {};
    autoFilledProps.forEach(p => {
        additionalProps[p] = props[p];
    });
    serializedValue[PROP_VALUE] =
        (await supportedTypes[type]?.serialize(
            engine,
            value,
            additionalProps
        )) || value;
    return serializedValue;
};
