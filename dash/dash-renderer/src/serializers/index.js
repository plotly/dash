import {type, prop} from 'ramda';
import DataFrameSerializer from './dataframe/fastparquet.dataframe';
import {ArrowDataFrameSerializer} from './dataframe/pyarrow.dataframe';
import DictDataFrameSerializer from './dataframe/dict.dataframe';

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
            if (type === 'pd.DataFrame') {
                // TODO: await `deserialize` as it might take time?
                if (engine == 'pyarrow') {
                    markedLayout.props[key] =
                        ArrowDataFrameSerializer.deserialize(originalValue);
                } else if (engine == 'fastparquet') {
                    markedLayout.props[key] =
                        DataFrameSerializer.deserialize(originalValue);
                } else if (engine == 'to_dict') {
                    markedLayout.props[key] =
                        DictDataFrameSerializer.deserialize(originalValue);
                }
            } else markedLayout.props[key] = prop(PROP_VALUE, value);
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
    if (type == 'pd.DataFrame')
        serializedValue[PROP_VALUE] = DictDataFrameSerializer.serialize(value);
    else serializedValue[PROP_VALUE] = value;
    return JSON.stringify(serializedValue);
};
