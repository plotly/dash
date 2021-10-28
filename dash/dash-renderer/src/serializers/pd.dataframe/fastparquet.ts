const parquet = require('parquetjs-lite');
import {Buffer} from 'buffer/';

function u8array_create(data: string) {
    // See https://developer.mozilla.org/en-US/docs/Web/API/btoa for why this is
    // necessary.
    const byte_chars = atob(data);
    const byte_numbers = [];
    for (let index = 0; index < byte_chars.length; index++)
        byte_numbers.push(byte_chars.charCodeAt(index));
    const byte_array = new Uint8Array(byte_numbers);
    return byte_array;
}

function santizeColumnValues(s: any, r: any) {
    for (const [k, v] of Object.entries(r)) {
        switch (s.fields?.[k]?.primitiveType) {
            case 'INT64':
                r[k] = Number(v);
                break;
            default:
                break;
        }
    }
    return r;
}

const fromParquet = async (_parquetFile: string) => {
    const records: any[] = [];
    const parquetData = Buffer.from(u8array_create(_parquetFile));
    const reader = await parquet.ParquetReader.openBuffer(parquetData);
    const schema = reader.getSchema();
    const columns = schema.fieldList.map((field: {name: string}) => ({
        name: field.name,
        id: field.name
    }));
    const cursor = reader.getCursor();
    let record = await cursor.next();
    while (record) {
        record = santizeColumnValues(schema, record);
        records.push(record);
        record = await cursor.next();
    }
    reader.close();
    const result = [records, { columns }];
    return result;
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
