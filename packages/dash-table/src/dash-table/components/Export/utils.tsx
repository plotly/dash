import * as R from 'ramda';
import XLSX from 'xlsx';
import { Data } from 'dash-table/components/Table/props';

interface IMergeObject {
    s: {r: number, c: number};
    e: {r: number, c: number};
}

export function transformMultDimArray(array: (string | string[])[], maxLength: number): string[][] {
    const newArray: string[][] = array.map(row => {
        if (row instanceof Array && row.length < maxLength) {
            return row.concat(Array(maxLength - row.length).fill(''));
        }
        if (maxLength === 0 || maxLength === 1) {
            return [row];
        }
        if (row instanceof String || typeof(row) === 'string') {
            return Array(maxLength).fill(row);
        }
        return row;
    });
    return newArray;
}

export function getMergeRanges(array: string[][]) {
    let apiMergeArray: IMergeObject[] = [];
    const iForEachOuter = R.addIndex<(string[]), void>(R.forEach);
    const iForEachInner = R.addIndex<(string), void>(R.forEach);
    iForEachOuter((row: string[], rIndex: number) => {
        let dict: any = {};
        iForEachInner((cell: string, cIndex: number) => {
            if (!dict[cell]) {
                dict[cell] = {s: {r: rIndex, c: cIndex}, e: {r: rIndex, c: cIndex }};
            } else {
                if (cIndex === (dict[cell].e.c + 1)) {
                    dict[cell].e = {r: rIndex, c: cIndex};
                } else {
                    apiMergeArray.push(dict[cell]);
                    dict[cell] = {s: {r: rIndex, c: cIndex}, e: {r: rIndex, c: cIndex }};
                }
            }
        }, row);
        const objectsToMerge: IMergeObject[] = Object.values(dict);
        apiMergeArray = R.concat(apiMergeArray, objectsToMerge );
    }, array);
    return R.filter((item: IMergeObject) => item.s.c !== item.e.c || item.s.r !== item.e.r, apiMergeArray);
}

export function createWorkbook(ws: XLSX.WorkSheet) {
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'SheetJS');
    return wb;
}

export function createWorksheet(heading: string[][], data: Data, columnID: string[], exportHeader: string, mergeDuplicateHeaders: boolean ) {
    const ws = XLSX.utils.aoa_to_sheet(heading);
    if (exportHeader === 'display' || exportHeader === 'names' || exportHeader === 'none') {
        XLSX.utils.sheet_add_json(ws, data, {
            header: columnID,
            skipHeader: true,
            origin: heading.length
        });
        if (exportHeader === 'display' && mergeDuplicateHeaders) {
            ws['!merges'] = getMergeRanges(heading);
        }
    } else if (exportHeader === 'ids') {
        XLSX.utils.sheet_add_json(ws, data, { header: columnID });
    }
    return ws;
}

export function createHeadings(columnHeaders: (string | string[])[], maxLength: number) {
    const transformedArray = transformMultDimArray(columnHeaders, maxLength);
    return R.transpose(transformedArray);
}