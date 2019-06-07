import { memoizeOneFactory } from 'core/memoizer';

import { clearSelection } from 'dash-table/utils/actions';

import {
    Data,
    SetProps,
    TableAction
} from 'dash-table/components/Table/props';

export interface IPaginator {
    loadNext(): void;
    loadPrevious(): void;
}

export function lastPage(data: Data, page_size: number) {
    return Math.max(Math.ceil(data.length / page_size) - 1, 0);
}

function getBackEndPagination(
    page_current: number,
    setProps: SetProps
): IPaginator {
    return {
        loadNext: () => {
            page_current++;
            setProps({ page_current, ...clearSelection });
        },
        loadPrevious: () => {
            if (page_current <= 0) {
                return;
            }

            page_current--;
            setProps({ page_current, ...clearSelection });
        }
    };
}

function getFrontEndPagination(
    page_current: number,
    page_size: number,
    setProps: SetProps,
    data: Data
) {
    return {
        loadNext: () => {
            const maxPageIndex = lastPage(data, page_size);

            if (page_current >= maxPageIndex) {
                return;
            }

            page_current++;
            setProps({ page_current, ...clearSelection });
        },
        loadPrevious: () => {
            if (page_current <= 0) {
                return;
            }

            page_current--;
            setProps({ page_current, ...clearSelection });
        }
    };
}

function getNoPagination() {
    return {
        loadNext: () => { },
        loadPrevious: () => { }
    };
}

const getter = (
    page_action: TableAction,
    page_current: number,
    page_size: number,
    setProps: SetProps,
    data: Data
): IPaginator => {
    switch (page_action) {
        case TableAction.None:
            return getNoPagination();
        case TableAction.Native:
            return getFrontEndPagination(page_current, page_size, setProps, data);
        case TableAction.Custom:
            return getBackEndPagination(page_current, setProps);
        default:
            throw new Error(`Unknown pagination mode: '${page_action}'`);
    }
};

export default memoizeOneFactory(getter);
