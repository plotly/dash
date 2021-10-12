import {type, prop} from 'ramda';
import DataFrameSerializer from './pandas.dataframe';

const PROP_TYPE = '__type';
const PROP_VALUE = '__value';
const PROP_ENGINE = '__engine';
const PROP_ID = '__internal_id';

export const DASH_BOOK_KEEPER = '__dash_serialized_props';

export const createBookkeeper = layout => {
    const markedLayout = {...layout, [DASH_BOOK_KEEPER]: {}};
    const {
        props,
        props: {children}
    } = layout;
    if (type(children) === 'Array') {
        markedLayout.props.children = children.map(child =>
            // TODO: await `deserialize` as it might take time?
            createBookkeeper(child)
        );
    }

    if (type(children) === 'Object') {
        // TODO: await `deserialize` as it might take time?
        markedLayout.props.children = createBookkeeper(children);
    }

    Object.entries(props).forEach(([key, value]) => {
        if (prop(PROP_TYPE, value)) {
            const {
                [PROP_TYPE]: type,
                [PROP_ENGINE]: engine,
                [PROP_VALUE]: originalValue,
                [PROP_ID]: internalId
            } = value;
            markedLayout[DASH_BOOK_KEEPER][key] = {type, engine, internalId};
            if (type === DataFrameSerializer.Type)
                // TODO: await `deserialize` as it might take time?
                markedLayout.props[key] = DataFrameSerializer.deserialize(
                    originalValue,
                    engine
                );
            else markedLayout.props[key] = prop(PROP_VALUE, value);
        } else {
            markedLayout.props[key] = value;
        }
    });
    return markedLayout;
};

export const dashSerializeValue = async ({type, engine, internalId}, value) => {
    if (!type) return value;
    const serializedValue = {};
    serializedValue[PROP_TYPE] = type;
    serializedValue[PROP_ENGINE] = engine;
    serializedValue[PROP_ID] = internalId;
    if (type == DataFrameSerializer.Type)
        serializedValue[PROP_VALUE] = DataFrameSerializer.serialize(
            value,
            engine
        );
    else serializedValue[PROP_VALUE] = value;
    return JSON.stringify(serializedValue);
};
