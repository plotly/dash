import * as R from 'ramda';
import SheetClip from 'sheetclip';

import Clipboard from 'core/Clipboard';
import Logger from 'core/Logger';

import { ActiveCell, Columns, Data, SelectedCells } from 'dash-table/components/Table/props';
import applyClipboardToData from './applyClipboardToData';

export default class TableClipboardHelper {
    public static toClipboard(e: any, selectedCells: SelectedCells, columns: Columns, data: Data) {
        const selectedRows = R.uniq(R.pluck(0, selectedCells).sort((a, b) => a - b));
        const selectedCols: any = R.uniq(R.pluck(1, selectedCells).sort((a, b) => a - b));

        const df = R.slice(
            R.head(selectedRows) as any,
            R.last(selectedRows) as any + 1,
            data
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
        data: Data,
        overflowColumns: boolean = true,
        overflowRows: boolean = true
    ): { data: Data, columns: Columns } | void {
        const text = Clipboard.get(ev);
        Logger.trace('TableClipboard -- get clipboard data: ', text);

        if (!text) {
            return;
        }

        const values = SheetClip.prototype.parse(text);

        return applyClipboardToData(
            values,
            activeCell,
            derived_viewport_indices,
            columns,
            data,
            overflowColumns,
            overflowRows
        );
    }
}