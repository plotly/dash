import FastParquetDataFrameSerializer from './fastparquet';
import ArrowDataFrameSerializer from './pyarrow';
import DictDataFrameSerializer from './to_dict';

const supportedEngines = {
    pyarrow: ArrowDataFrameSerializer,
    fastparquet: FastParquetDataFrameSerializer,
    to_dict: DictDataFrameSerializer
};

export default {
    deserialize: (value, engine) =>
        supportedEngines[engine]?.deserialize(value) || value,
    serialize: (value, engine) =>
        supportedEngines[engine]?.serialize(value) || value
};
