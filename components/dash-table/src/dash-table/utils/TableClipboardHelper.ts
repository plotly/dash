import * as R from 'ramda';
import SheetClip from 'sheetclip';

import Clipboard from 'core/Clipboard';
import Logger from 'core/Logger';

import {
    ICellCoordinates,
    Columns,
    Data,
    SelectedCells
} from 'dash-table/components/Table/props';
import {createHeadings} from 'dash-table/components/Export/utils';
import applyClipboardToData from './applyClipboardToData';
import getHeaderRows from 'dash-table/derived/header/headerRows';

export default class TableClipboardHelper {
    private static lastLocalCopy: any[][] = [[]];
    private static localCopyWithoutHeaders: any[][] = [[]];

    public static toClipboard(
        e: any,
        selectedCells: SelectedCells,
        columns: Columns,
        visibleColumns: Columns,
        data: Data,
        includeHeaders: boolean
    ) {
        const selectedRows = R.uniq(
            R.pluck('row', selectedCells).sort((a, b) => a - b)
        );
        const selectedCols: any = R.uniq(
            R.pluck('column', selectedCells).sort((a, b) => a - b)
        );

        const df = R.slice(
            R.head(selectedRows) as any,
            (R.last(selectedRows) as any) + 1,
            data
        ).map(row =>
            R.props(
                selectedCols,
                R.props(R.pluck('id', visibleColumns) as any, row) as any
            )
        );

        let value = SheetClip.prototype.stringify(df);
        TableClipboardHelper.lastLocalCopy = df;

        if (includeHeaders) {
            const transposedHeaders = createHeadings(
                R.pluck('name', visibleColumns),
                getHeaderRows(columns)
            );
            const headers: any = R.map(
                (row: string[]) =>
                    R.map((index: number) => row[index], selectedCols),
                transposedHeaders
            );
            const dfHeaders = headers.concat(df);
            value = SheetClip.prototype.stringify(dfHeaders);
            TableClipboardHelper.lastLocalCopy = dfHeaders;
            TableClipboardHelper.localCopyWithoutHeaders = df;
        }

        Logger.trace('TableClipboard -- set clipboard data: ', value);

        Clipboard.set(e, value);
    }

    public static clearClipboard() {
        TableClipboardHelper.lastLocalCopy = [];
        TableClipboardHelper.localCopyWithoutHeaders = [];
    }

    public static fromClipboard(
        ev: ClipboardEvent,
        activeCell: ICellCoordinates,
        derived_viewport_indices: number[],
        columns: Columns,
        visibleColumns: Columns,
        data: Data,
        overflowColumns = true,
        overflowRows = true,
        includeHeaders: boolean
    ): {data: Data; columns: Columns} | void {
        const text = Clipboard.get(ev);
        Logger.trace('TableClipboard -- get clipboard data: ', text);

        if (!text) {
            return;
        }

        const localDf = SheetClip.prototype.stringify(
            TableClipboardHelper.lastLocalCopy
        );
        const localCopy = includeHeaders
            ? TableClipboardHelper.localCopyWithoutHeaders
            : TableClipboardHelper.lastLocalCopy;
        const values =
            localDf === text ? localCopy : TableClipboardHelper.parse(text);

        return applyClipboardToData(
            values,
            activeCell,
            derived_viewport_indices,
            columns,
            visibleColumns,
            data,
            overflowColumns,
            overflowRows
        );
    }

    private static parse(str: string) {
        let r,
            rlen,
            a = 0,
            c,
            clen,
            multiline,
            last,
            arr: string[][] = [[]];
        const rows = str.split('\n');
        if (rows.length > 1 && rows[rows.length - 1] === '') {
            rows.pop();
        }
        arr = [];
        for (r = 0, rlen = rows.length; r < rlen; r += 1) {
            const row = rows[r].split('\t');
            for (c = 0, clen = row.length; c < clen; c += 1) {
                if (!arr[a]) {
                    arr[a] = [];
                }
                if (multiline && c === 0) {
                    last = arr[a].length - 1;
                    arr[a][last] =
                        arr[a][last] + '\n' + row[0].replace(/""/g, '"');
                    if (
                        multiline &&
                        TableClipboardHelper.countQuotes(row[0]) & 1
                    ) {
                        multiline = false;
                        arr[a][last] = arr[a][last].substring(
                            0,
                            arr[a][last].length - 1
                        );
                    }
                } else {
                    if (
                        c === clen - 1 &&
                        row[c].indexOf('"') === 0 &&
                        TableClipboardHelper.countQuotes(row[c]) & 1
                    ) {
                        arr[a].push(row[c].substring(1).replace(/""/g, '"'));
                        multiline = true;
                    } else {
                        arr[a].push(row[c]);
                        multiline = false;
                    }
                }
            }
            if (!multiline) {
                a += 1;
            }
        }
        return arr;
    }

    private static countQuotes(str: string) {
        return str.split('"').length - 1;
    }
}
