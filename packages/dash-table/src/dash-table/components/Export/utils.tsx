import * as R from 'ramda';
import {WorkBook} from 'xlsx/types';

import {Data, ExportHeaders} from 'dash-table/components/Table/props';
import LazyLoader from 'dash-table/LazyLoader';

interface IMergeObject {
    s: {r: number; c: number};
    e: {r: number; c: number};
}

export function transformMultiDimArray(
    array: (string | string[])[],
    maxLength: number
): string[][] {
    const newArray: string[][] = array.map(row => {
        if (row instanceof Array && row.length < maxLength) {
            return row.concat(Array(maxLength - row.length).fill(''));
        }
        if (maxLength === 0 || maxLength === 1) {
            return [row];
        }
        if (row instanceof String || typeof row === 'string') {
            return Array(maxLength).fill(row);
        }
        return row;
    });
    return newArray;
}

export function getMergeRanges(array: string[][]) {
    let apiMergeArray: IMergeObject[] = [];
    const iForEachOuter = R.addIndex<string[], void>(R.forEach);
    const iForEachInner = R.addIndex<string, void>(R.forEach);
    iForEachOuter((row: string[], rIndex: number) => {
        const dict: any = {};
        iForEachInner((cell: string, cIndex: number) => {
            if (!dict[cell]) {
                dict[cell] = {
                    s: {r: rIndex, c: cIndex},
                    e: {r: rIndex, c: cIndex}
                };
            } else {
                if (cIndex === dict[cell].e.c + 1) {
                    dict[cell].e = {r: rIndex, c: cIndex};
                } else {
                    apiMergeArray.push(dict[cell]);
                    dict[cell] = {
                        s: {r: rIndex, c: cIndex},
                        e: {r: rIndex, c: cIndex}
                    };
                }
            }
        }, row);
        const objectsToMerge: IMergeObject[] = Object.values(dict);
        apiMergeArray = R.concat(apiMergeArray, objectsToMerge);
    }, array);
    return R.filter(
        (item: IMergeObject) => item.s.c !== item.e.c || item.s.r !== item.e.r,
        apiMergeArray
    );
}

export async function createWorkbook(
    heading: string[][],
    data: Data,
    columnID: string[],
    exportHeader: string,
    mergeDuplicateHeaders: boolean
) {
    const XLSX = await LazyLoader.xlsx;

    const ws = XLSX.utils.aoa_to_sheet([]);

    data = R.map(R.pick(columnID))(data);

    if (
        exportHeader === ExportHeaders.Display ||
        exportHeader === ExportHeaders.Names ||
        exportHeader === ExportHeaders.None
    ) {
        XLSX.utils.sheet_add_json(ws, heading, {skipHeader: true});

        const contentOptions =
            heading.length > 0
                ? {header: columnID, skipHeader: true, origin: heading.length}
                : {skipHeader: true};

        XLSX.utils.sheet_add_json(ws, data, contentOptions);

        if (exportHeader === ExportHeaders.Display && mergeDuplicateHeaders) {
            ws['!merges'] = getMergeRanges(heading);
        }
    } else if (exportHeader === ExportHeaders.Ids) {
        XLSX.utils.sheet_add_json(ws, data, {header: columnID});
    }

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'SheetJS');
    return wb;
}

export async function exportWorkbook(wb: WorkBook, format: string) {
    const XLSX = await LazyLoader.xlsx;

    if (format === 'xlsx') {
        XLSX.writeFile(wb, 'Data.xlsx', {bookType: 'xlsx', type: 'buffer'});
    } else if (format === 'csv') {
        XLSX.writeFile(wb, 'Data.csv', {bookType: 'csv', type: 'buffer'});
    }
}

export function createHeadings(
    columnHeaders: (string | string[])[],
    maxLength: number
) {
    const transformedArray = transformMultiDimArray(columnHeaders, maxLength);
    return R.transpose(transformedArray);
}
