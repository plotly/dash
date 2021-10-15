// import parquet from 'parquetjs';
// import { Buffer } from 'buffer/';

/*
    WARNING! UNTESTED CODE!!!

    Things to test
    1. fromParquet() func
        Sample input:   // equivalent to to_dict("records")= [{'x': 0.0, 'y': 4.0}, {'x': 1.0, 'y': 5.0}, {'x': 2.0, 'y': 6.0}, {'x': 3.0, 'y': 7.0}]
            parquetFile=UEFSMRUAFVwVTiwVCBUAFQYVCAAAH8KLCAAAAAAAAMO/Y2JgYMOgYGRAAR/DrMKhDAcIw4XDoQDCkwEAwpzDv8KZNC4AAAAVABVcFVQsFQgVABUGFQgAAB/CiwgAAAAAAADDv2NiYGDDoGBkAAMBBwgtAsKlJcKgwrQMwpRmYAAAw6wjR1UuAAAAFQIZPEgGc2NoZW1hFQQAFQoVwoABFQIYAXgAFQoVwoABFQIYAXkAFggZHBksJngcFQoZFQAZGAF4FQQWCBZ+FnAZDBYIPBgIAAAAAAAACEAYCAAAAAAAAAAAFgAAGRwVABUAFQIAAAAmw64BHBUKGRUAGRgBeRUEFggWfhZ2GQwWeDwYCAAAAAAAABxAGAgAAAAAAAAQQBYAABkcFQAVABUCAAAAFsO8ARYIABkcGAZwYW5kYXMYwqIEeyJjb2x1bW5faW5kZXhlcyI6IFt7ImZpZWxkX25hbWUiOiBudWxsLCAibWV0YWRhdGEiOiBudWxsLCAibmFtZSI6IG51bGwsICJudW1weV90eXBlIjogIm9iamVjdCIsICJwYW5kYXNfdHlwZSI6ICJtaXhlZC1pbnRlZ2VyIn1dLCAiY29sdW1ucyI6IFt7ImZpZWxkX25hbWUiOiAieCIsICJtZXRhZGF0YSI6IG51bGwsICJuYW1lIjogIngiLCAibnVtcHlfdHlwZSI6ICJmbG9hdDY0IiwgInBhbmRhc190eXBlIjogImZsb2F0NjQifSwgeyJmaWVsZF9uYW1lIjogInkiLCAibWV0YWRhdGEiOiBudWxsLCAibmFtZSI6ICJ5IiwgIm51bXB5X3R5cGUiOiAiZmxvYXQ2NCIsICJwYW5kYXNfdHlwZSI6ICJmbG9hdDY0In1dLCAiY3JlYXRvciI6IHsibGlicmFyeSI6ICJmYXN0cGFycXVldCIsICJ2ZXJzaW9uIjogIjAuNy4xIn0sICJpbmRleF9jb2x1bW5zIjogW3sia2luZCI6ICJyYW5nZSIsICJuYW1lIjogbnVsbCwgInN0YXJ0IjogMCwgInN0ZXAiOiAxLCAic3RvcCI6IDR9XSwgInBhbmRhc192ZXJzaW9uIjogIjEuMy4zIiwgInBhcnRpdGlvbl9jb2x1bW5zIjogW119ABgsZmFzdHBhcnF1ZXQtcHl0aG9uIHZlcnNpb24gMS4wLjAgKGJ1aWxkIDExMSkABwMAAFBBUjE=
            engine=fastparquet

    2. toParquet() func
*/

const fromParquet = async (_parquetFile: string) => {
    const records: any[] = [];
    // const parquetData = Buffer.from(atob(parquetFile));
    // const reader = await parquet.ParquetReader.openBuffer(parquetData);
    // console.log(reader)
    // const cursor = reader.getCursor();
    // let record = null;
    // do {
    //     record = await cursor.next();
    //     records.push(record);
    // } while (record);
    // reader.close();
    return records;
};

// const transformPromise = (
//     t: {
//         _transform: (
//             arg0: any,
//             arg1: any,
//             arg2: (error: any, data: any) => void
//         ) => void;
//     },
//     d: any,
//     e: any
// ) => {
//     new Promise((resolve, reject) => {
//         t._transform(d, e, (error: any, data: unknown) => {
//             if (!error) resolve(data);
//             else reject();
//         });
//     });
// };

// const flushPromise = (t: {
//     _flush: (arg0: (error: any, data: any) => void) => void;
// }) =>
//     new Promise((resolve, reject) =>
//         t._flush((error: any, data: string) => {
//             if (!error) resolve(btoa(data));
//             else reject();
//         })
//     );

const toParquet = async (_records: any, _engine: any) => {
    // const schema = {},
    //     opts = {};
    // const transformer = new parquet.ParquetTransformer(schema, opts);
    // await Promise.allSettled(
    //     records.map((record: any) =>
    //         transformPromise(transformer, record, 'utf-8')
    //     )
    // );
    // return await flushPromise(transformer);
};

export default {
    serialize: toParquet,
    deserialize: fromParquet
};
