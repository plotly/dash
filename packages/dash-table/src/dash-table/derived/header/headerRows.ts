import { VisibleColumns } from 'dash-table/components/Table/props';

const getColLength = (c: any) => (Array.isArray(c.name) ? c.name.length : 1);

export default (
    columns: VisibleColumns
): number => Math.max(...columns.map(getColLength));