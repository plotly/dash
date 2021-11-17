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

function sanitizeColumnValues(s: any, r: any) {
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
        record = sanitizeColumnValues(schema, record);
        records.push(record);
        record = await cursor.next();
    }
    reader.close();
    const result = [records, {columns, schema}];
    return result;
};

const transformPromise = (t: any, d: any, e: any) =>
    new Promise((resolve, reject) => {
        t._transform(d, e, (error: any, data: any) => {
            if (!error) resolve(data);
            else reject(error);
        });
    });

const flushPromise = (t: any) =>
    new Promise((resolve, reject) =>
        t._flush((error: any, data: string) => {
            if (!error) resolve(btoa(data));
            else reject();
        })
    );

const toParquet = async (args: any) => {
    const [records, additionalProps] = args;
    const schema = additionalProps.schema;
    const opts = {};
    const transformer = new parquet.ParquetTransformer(schema, opts);
    await Promise.allSettled(
        records.map((record: any) =>
            transformPromise(transformer, record, 'utf-8')
        )
    );
    const result = await flushPromise(transformer);
    return result;
};

export default {
    serialize: toParquet,
    deserialize: fromParquet
};
