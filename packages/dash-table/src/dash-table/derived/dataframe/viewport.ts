import { memoizeOneFactory } from 'core/memoizer';

import {
    Dataframe,
    Indices,
    IPaginationSettings,
    PaginationMode,
    IDerivedDataframe
} from 'dash-table/components/Table/props';

function getNoPagination(dataframe: Dataframe, indices: Indices): IDerivedDataframe {
    return { dataframe, indices };
}

function getFrontEndPagination(settings: IPaginationSettings, dataframe: Dataframe, indices: Indices): IDerivedDataframe {
    let currentPage = Math.min(
        settings.current_page,
        Math.floor(dataframe.length / settings.page_size)
    );

    const firstIndex = settings.page_size * currentPage;
    const lastIndex = Math.min(
        firstIndex + settings.displayed_pages * settings.page_size,
        dataframe.length
    );

    return {
        dataframe: dataframe.slice(firstIndex, lastIndex),
        indices: indices.slice(firstIndex, lastIndex)
    };
}

function getBackEndPagination(dataframe: Dataframe, indices: Indices): IDerivedDataframe {
    return { dataframe, indices };
}

const getter = (
    pagination_mode: PaginationMode,
    pagination_settings: IPaginationSettings,
    dataframe: Dataframe,
    indices: Indices
): IDerivedDataframe => {
    switch (pagination_mode) {
        case false:
            return getNoPagination(dataframe, indices);
        case true:
        case 'fe':
            return getFrontEndPagination(pagination_settings, dataframe, indices);
        case 'be':
            return getBackEndPagination(dataframe, indices);
        default:
            throw new Error(`Unknown pagination mode: '${pagination_mode}'`);
    }
};

export default memoizeOneFactory(getter);
