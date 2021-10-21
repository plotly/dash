import FastParquetDataFrameSerializer from './fastparquet';
import ArrowDataFrameSerializer from './pyarrow';
import DictDataFrameSerializer from './to_dict';

const supportedEngines = {
    pyarrow: ArrowDataFrameSerializer,
    fastparquet: FastParquetDataFrameSerializer,
    to_dict: DictDataFrameSerializer
};

export default {
    serialize: (engine, ...args) =>
        supportedEngines[engine]?.serialize(args) || args,
    deserialize: (engine, arg) =>
        supportedEngines[engine]?.deserialize(arg) || [arg]
};
