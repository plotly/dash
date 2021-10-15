// import {Table, Vector} from 'apache-arrow';
// import {StructRow} from 'apache-arrow/vector/row';

/** Data types used by ArrowJS. */
export type DataType =
    | null
    | boolean
    | number
    | string
    | Date // datetime
    | Int32Array // int
    | Uint8Array; // bytes
// | Vector // arrays
// | StructRow; // interval

export interface ArrowDataframeProto {
    data: ArrowTableProto;
    height: string;
    width: string;
}

export interface ArrowTableProto {
    data: Uint8Array;
    index: Uint8Array;
    columns: Uint8Array;
}

export class ArrowDataFrameSerializer {
    static deserialize = (_value: string) => {
        // const dataBuffer: Uint8Array = new TextEncoder().encode(atob(value));
        // console.log('dataBuffer = ', dataBuffer);
        // const arTable = Table.from(dataBuffer);
        // console.log('arTable = ', arTable);
        // const records = arTable.toArray();
        // console.log('ArrowTable.toArray() = ', records);
        // return records;
        return [];
    };

    static serialize = () => {};
}
