import { memoizeOneFactory } from 'core/memoizer';

import {
    Data,
    Indices,
    IPaginationSettings,
    PaginationMode,
    IDerivedData
} from 'dash-table/components/Table/props';

function getNoPagination(data: Data, indices: Indices): IDerivedData {
    return { data, indices };
}

function getFrontEndPagination(settings: IPaginationSettings, data: Data, indices: Indices): IDerivedData {
    let currentPage = Math.min(
        settings.current_page,
        Math.floor(data.length / settings.page_size)
    );

    const firstIndex = settings.page_size * currentPage;
    const lastIndex = Math.min(
        firstIndex + settings.displayed_pages * settings.page_size,
        data.length
    );

    return {
        data: data.slice(firstIndex, lastIndex),
        indices: indices.slice(firstIndex, lastIndex)
    };
}

function getBackEndPagination(data: Data, indices: Indices): IDerivedData {
    return { data, indices };
}

const getter = (
    pagination_mode: PaginationMode,
    pagination_settings: IPaginationSettings,
    data: Data,
    indices: Indices
): IDerivedData => {
    switch (pagination_mode) {
        case false:
            return getNoPagination(data, indices);
        case true:
        case 'fe':
            return getFrontEndPagination(pagination_settings, data, indices);
        case 'be':
            return getBackEndPagination(data, indices);
        default:
            throw new Error(`Unknown pagination mode: '${pagination_mode}'`);
    }
};

export default memoizeOneFactory(getter);
