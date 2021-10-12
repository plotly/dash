import parquet from 'parquetjs-lite';

/*
    WARNING! UNTESTED CODE!!!

    Things to test
    1. fromParquet() func
        Sample input:   // equivalent to to_dict("records")= [{'x': 0.0, 'y': 4.0}, {'x': 1.0, 'y': 5.0}, {'x': 2.0, 'y': 6.0}, {'x': 3.0, 'y': 7.0}]
            parquetFile=UEFSMRUAFVwVTiwVCBUAFQYVCAAAH8KLCAAAAAAAAMO/Y2JgYMOgYGRAAR/DrMKhDAcIw4XDoQDCkwEAwpzDv8KZNC4AAAAVABVcFVQsFQgVABUGFQgAAB/CiwgAAAAAAADDv2NiYGDDoGBkAAMBBwgtAsKlJcKgwrQMwpRmYAAAw6wjR1UuAAAAFQIZPEgGc2NoZW1hFQQAFQoVwoABFQIYAXgAFQoVwoABFQIYAXkAFggZHBksJngcFQoZFQAZGAF4FQQWCBZ+FnAZDBYIPBgIAAAAAAAACEAYCAAAAAAAAAAAFgAAGRwVABUAFQIAAAAmw64BHBUKGRUAGRgBeRUEFggWfhZ2GQwWeDwYCAAAAAAAABxAGAgAAAAAAAAQQBYAABkcFQAVABUCAAAAFsO8ARYIABkcGAZwYW5kYXMYwqIEeyJjb2x1bW5faW5kZXhlcyI6IFt7ImZpZWxkX25hbWUiOiBudWxsLCAibWV0YWRhdGEiOiBudWxsLCAibmFtZSI6IG51bGwsICJudW1weV90eXBlIjogIm9iamVjdCIsICJwYW5kYXNfdHlwZSI6ICJtaXhlZC1pbnRlZ2VyIn1dLCAiY29sdW1ucyI6IFt7ImZpZWxkX25hbWUiOiAieCIsICJtZXRhZGF0YSI6IG51bGwsICJuYW1lIjogIngiLCAibnVtcHlfdHlwZSI6ICJmbG9hdDY0IiwgInBhbmRhc190eXBlIjogImZsb2F0NjQifSwgeyJmaWVsZF9uYW1lIjogInkiLCAibWV0YWRhdGEiOiBudWxsLCAibmFtZSI6ICJ5IiwgIm51bXB5X3R5cGUiOiAiZmxvYXQ2NCIsICJwYW5kYXNfdHlwZSI6ICJmbG9hdDY0In1dLCAiY3JlYXRvciI6IHsibGlicmFyeSI6ICJmYXN0cGFycXVldCIsICJ2ZXJzaW9uIjogIjAuNy4xIn0sICJpbmRleF9jb2x1bW5zIjogW3sia2luZCI6ICJyYW5nZSIsICJuYW1lIjogbnVsbCwgInN0YXJ0IjogMCwgInN0ZXAiOiAxLCAic3RvcCI6IDR9XSwgInBhbmRhc192ZXJzaW9uIjogIjEuMy4zIiwgInBhcnRpdGlvbl9jb2x1bW5zIjogW119ABgsZmFzdHBhcnF1ZXQtcHl0aG9uIHZlcnNpb24gMS4wLjAgKGJ1aWxkIDExMSkABwMAAFBBUjE=
            engine=fastparquet

    2. toParquet() func
*/

const fromParquet = async (parquetFile, engine) => {
    const records = [];
    const parquetData = atob(parquetFile);
    if (engine === 'fastparquet') {
        let reader = await parquet.ParquetReader.openBuffer(parquetData);
        let cursor = reader.getCursor();
        let record = null;
        do {
            record = await cursor.next();
            records.push(record);
        } while (record);
        reader.close();
    } else {
        return records;
    }
    return records;
};

const transformPromise = (t, d, e) => {
    new Promise((resolve, reject) => {
        t._transform(d, e, (error, data) => {
            if (!error) resolve(data);
            else reject();
        });
    });
};

const flushPromise = t =>
    new Promise((resolve, reject) =>
        t._flush((error, data) => {
            if (!error) resolve(btoa(data));
            else reject();
        })
    );

const toParquet = async (records, engine) => {
    if (engine === 'fastparquet') {
        const schema = {},
            opts = {};
        const transformer = new parquet.ParquetTransformer(schema, opts);
        await Promise.allSettled(
            records.map(record =>
                transformPromise(transformer, record, 'utf-8')
            )
        );
        return await flushPromise(transformer);
    }
    return '';
};

export const Type = 'pd.DataFrame';
export const serialize = toParquet;
export const deserialize = fromParquet;
