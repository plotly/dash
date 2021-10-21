export default class DictDataFrameSerializer {
    static serialize = args => {
        const [value, additionalProps] = args;
        return {
            records: value,
            columns: additionalProps?.['columns']?.map(col => col.name)
        };
    };
    static deserialize = value => {
        const {columns, records} = value;
        return [records, {columns: columns.map(col => ({name: col, id: col}))}];
    };
}
