const parquet = require('parquetjs-lite');
import {Buffer} from 'buffer/';

const fromParquet = async (_parquetFile: string) => {
    const records: any[] = [];
    const parquetData = Buffer.from(atob(_parquetFile));
    const reader = await parquet.ParquetReader.openBuffer(parquetData);
    console.log(reader);
    const cursor = reader.getCursor();
    let record = null;
    do {
        record = await cursor.next();
        records.push(record);
    } while (record);
    reader.close();
    return records;
};

const transformPromise = (
    t: {
        _transform: (
            arg0: any,
            arg1: any,
            arg2: (error: any, data: any) => void
        ) => void;
    },
    d: any,
    e: any
) => {
    new Promise((resolve, reject) => {
        t._transform(d, e, (error: any, data: unknown) => {
            if (!error) resolve(data);
            else reject();
        });
    });
};

const flushPromise = (t: {
    _flush: (arg0: (error: any, data: any) => void) => void;
}) =>
    new Promise((resolve, reject) =>
        t._flush((error: any, data: string) => {
            if (!error) resolve(btoa(data));
            else reject();
        })
    );

const toParquet = async (_records: any, _engine: any) => {
    const schema = {},
        opts = {};
    const transformer = new parquet.ParquetTransformer(schema, opts);
    await Promise.allSettled(
        _records.map((record: any) =>
            transformPromise(transformer, record, 'utf-8')
        )
    );
    return await flushPromise(transformer);
};

export default {
    serialize: toParquet,
    deserialize: fromParquet
};
