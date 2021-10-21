import {type, prop} from 'ramda';
import DataFrameSerializer from './pd.dataframe';

const PROP_TYPE = '__type';
const PROP_VALUE = '__value';
const PROP_ENGINE = '__engine';
const supportedTypes = {
    'pd.DataFrame': DataFrameSerializer
};

export const SERIALIZER_BOOKKEEPER = '__dash_serialized_props';
export const deserializeLayout = layout => {
    const markedLayout = {...layout, [SERIALIZER_BOOKKEEPER]: {}};
    const {
        props,
        props: {children}
    } = layout;
    if (type(children) === 'Array')
        markedLayout.props.children = children.map(child =>
            deserializeLayout(child)
        );

    if (type(children) === 'Object')
        markedLayout.props.children = deserializeLayout(children);

    Object.entries(props).forEach(([key, value]) => {
        if (prop(PROP_TYPE, value)) {
            deserializeValue(markedLayout, key, value);
        } else {
            markedLayout.props[key] = value;
        }
    });
    return markedLayout;
};

const deserializeValue = (
    layout,
    key,
    {[PROP_TYPE]: type, [PROP_ENGINE]: engine, [PROP_VALUE]: originalValue}
) => {
    layout[SERIALIZER_BOOKKEEPER][key] = {type, engine};
    const [val, missingProps] = supportedTypes[type]?.deserialize(
        engine,
        originalValue
    ) || [originalValue, {}];
    layout.props[key] = val;
    for (const k in missingProps) {
        layout.props[k] = missingProps[k];
    }
};

export const serializeValue = ({type, engine}, value, props) => {
    if (!type) return value;
    const serializedValue = {};
    serializedValue[PROP_TYPE] = type;
    serializedValue[PROP_ENGINE] = engine;
    serializedValue[PROP_VALUE] =
        supportedTypes[type]?.serialize(engine, value, props) || value;
    return serializedValue;
};
