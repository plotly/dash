import * as R from 'ramda';
import SheetClip from 'sheetclip';

import Clipboard from 'core/Clipboard';
import Logger from 'core/Logger';

import { colIsEditable } from 'dash-table/components/derivedState';
import { ActiveCell, Columns, Dataframe, SelectedCells, ColumnType } from 'dash-table/components/Table/props';

export default class TableClipboardHelper {
    public static toClipboard(e: any, selectedCells: SelectedCells, columns: Columns, dataframe: Dataframe) {
        const selectedRows = R.uniq(R.pluck(0, selectedCells).sort((a, b) => a - b));
        const selectedCols: any = R.uniq(R.pluck(1, selectedCells).sort((a, b) => a - b));

        const df = R.slice(
            R.head(selectedRows) as any,
            R.last(selectedRows) as any + 1,
            dataframe
        ).map(row =>
            R.props(selectedCols, R.props(R.pluck('id', columns) as any, row) as any)
        );

        const value = SheetClip.prototype.stringify(df);

        Logger.trace('TableClipboard -- set clipboard data: ', value);

        Clipboard.set(e, value);
    }

    public static fromClipboard(
        ev: ClipboardEvent,
        activeCell: ActiveCell,
        derived_viewport_indices: number[],
        columns: Columns,
        dataframe: Dataframe,
        overflowColumns: boolean = true,
        overflowRows: boolean = true
    ): { dataframe: Dataframe, columns: Columns } | void {
        const text = Clipboard.get(ev);
        Logger.trace('TableClipboard -- get clipboard data: ', text);

        if (!text) {
            return;
        }

        if (!overflowRows) {
            Logger.debug(`Clipboard -- Sorting or filtering active, do not create new rows`);
        }

        if (!overflowColumns) {
            Logger.debug(`Clipboard -- Do not create new columns`);
        }

        const values = SheetClip.prototype.parse(text);

        let newDataframe = dataframe;
        const newColumns = columns;

        if (overflowColumns && values[0].length + activeCell[1] >= columns.length) {
            for (
                let i = columns.length;
                i < values[0].length + activeCell[1];
                i++
            ) {
                newColumns.push({
                    id: `Column ${i + 1}`,
                    name: `Column ${i + 1}`,
                    type: ColumnType.Text
                });
                newDataframe.forEach(row => (row[`Column ${i}`] = ''));
            }
        }

        const realActiveRow = derived_viewport_indices[activeCell[0]];
        if (overflowRows && values.length + realActiveRow >= dataframe.length) {
            const emptyRow: any = {};
            columns.forEach(c => (emptyRow[c.id] = ''));
            newDataframe = R.concat(
                newDataframe,
                R.repeat(
                    emptyRow,
                    values.length + realActiveRow - dataframe.length
                )
            );
        }

        values.forEach((row: string[], i: number) =>
            row.forEach((cell: string, j: number) => {
                const iOffset = activeCell[0] + i;
                if (derived_viewport_indices.length <= activeCell[0] + i) {
                    return;
                }
                const iRealCell = derived_viewport_indices[iOffset];

                const jOffset = activeCell[1] + j;
                const col = newColumns[jOffset];
                if (col && colIsEditable(true, col)) {
                    newDataframe = R.set(
                        R.lensPath([iRealCell, col.id]),
                        cell,
                        newDataframe
                    );
                }
            })
        );

        return { dataframe: newDataframe, columns: newColumns };
    }
}