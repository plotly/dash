import { IVisibleColumn } from 'dash-table/components/Table/props';

export default (
    editable: boolean,
    column: IVisibleColumn
): boolean => editable && (column.editable === undefined || column.editable);