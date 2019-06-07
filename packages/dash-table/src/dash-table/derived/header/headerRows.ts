import { IColumn } from 'dash-table/components/Table/props';

const getColLength = (c: IColumn) => c.hidden ?
    0 :
    Array.isArray(c.name) ?
        c.name.length :
        1;

export default (
    columns: IColumn[]
): number => Math.max(...columns.map(getColLength));