import DictDataFrameSerializer from './to_dict';

const supportedEngines = {
    to_dict: DictDataFrameSerializer
};

export default {
    serialize: (engine, ...args) =>
        supportedEngines[engine]?.serialize(args) || args,
    deserialize: (engine, arg) =>
        supportedEngines[engine]?.deserialize(arg) || [arg]
};
