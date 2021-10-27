function encodeField(key, value) {
    switch (key) {
        case 'columns':
            return value.map(col => col.name);
        default:
            return value;
    }
}

function decodeField(key, value) {
    switch (key) {
        case 'columns':
            return value.map(col => ({name: col, id: col}));
        default:
            return value;
    }
}

export default class DictDataFrameSerializer {
    static serialize = args => {
        const [value, additionalProps] = args;
        const result = {records: value};
        additionalProps.forEach(prop => {
            for (const [key, value] of Object.entries(prop)) {
                result[key] = encodeField(key, value);
            }
        });
        return result;
    };
    static deserialize = value => {
        const {records, ...additionalProps} = value;
        const result = [records];
        for (const [key, value] of Object.entries(additionalProps)) {
            result.push({[key]: decodeField(key, value)});
        }
        return result;
    };
}
