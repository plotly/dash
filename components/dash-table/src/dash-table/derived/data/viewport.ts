import {memoizeOneFactory} from 'core/memoizer';
import {lastPage} from 'dash-table/derived/paginator';

import {
    Data,
    Indices,
    IDerivedData,
    TableAction
} from 'dash-table/components/Table/props';

function getNoPagination(data: Data, indices: Indices): IDerivedData {
    return {data, indices};
}

function getFrontEndPagination(
    page_current: number,
    page_size: number,
    data: Data,
    indices: Indices
): IDerivedData {
    const currentPage = Math.min(page_current, lastPage(data, page_size));

    const firstIndex = page_size * currentPage;
    const lastIndex = Math.min(firstIndex + page_size, data.length);

    return {
        data: data.slice(firstIndex, lastIndex),
        indices: indices.slice(firstIndex, lastIndex)
    };
}

function getBackEndPagination(data: Data, indices: Indices): IDerivedData {
    return {data, indices};
}

const getter = (
    page_action: TableAction,
    page_current: number,
    page_size: number,
    data: Data,
    indices: Indices
): IDerivedData => {
    switch (page_action) {
        case TableAction.None:
            return getNoPagination(data, indices);
        case TableAction.Native:
            return getFrontEndPagination(
                page_current,
                page_size,
                data,
                indices
            );
        case TableAction.Custom:
            return getBackEndPagination(data, indices);
        default:
            throw new Error(`Unknown pagination mode: '${page_action}'`);
    }
};

export default memoizeOneFactory(getter);
