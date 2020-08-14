import {Selection} from 'dash-table/components/Table/props';

export default (
    fixedColumns: number,
    rowDeletable: boolean,
    rowSelectable: Selection
): number => {
    const offset = (rowDeletable ? 1 : 0) + (rowSelectable ? 1 : 0);

    return Math.max(0, fixedColumns - offset);
};
