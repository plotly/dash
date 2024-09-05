import {memoizeOneFactory} from 'core/memoizer';

import {clearSelection} from 'dash-table/utils/actions';

import {Data, SetProps, TableAction} from 'dash-table/components/Table/props';

export interface IPaginator {
    loadNext(): void;
    loadPrevious(): void;
    loadFirst(): void;
    loadLast(): void;
    loadPage(page: number): void;
    hasPrevious(): boolean;
    hasNext(): boolean;
    isLast(): boolean;
    lastPage: number | undefined;
}

export interface IPaginatorParams {
    setProps: SetProps;
    page_current: number;
    page_count: number | undefined;
}

export function lastPage(data: Data, page_size: number) {
    return Math.ceil(data.length / page_size);
}

function makePaginator(params: IPaginatorParams | null): IPaginator {
    if (params === null) {
        return {
            loadNext() {},
            loadPrevious() {},
            loadFirst() {},
            loadLast() {},
            loadPage() {},
            hasPrevious() {
                return true;
            },
            hasNext() {
                return true;
            },
            isLast() {
                return false;
            },
            lastPage: undefined
        };
    }

    const {setProps, page_count} = params;
    let {page_current} = params;

    if (page_count && page_count - 1 < page_current) {
        page_current = 0;
        updatePage();
    }

    function updatePage() {
        setProps({
            page_current,
            ...clearSelection
        });
    }

    function loadPage(page: number) {
        page = Math.max(0, page);
        page = page_count ? Math.min(page_count - 1, page) : page;

        page_current = page;
        updatePage();
    }

    return {
        loadNext: () => loadPage(page_current + 1),

        loadPrevious: () => loadPage(page_current - 1),

        loadFirst: () => loadPage(0),

        loadPage,

        loadLast: () => {
            if (page_count) {
                loadPage(page_count - 1);
            }
        },

        hasPrevious: () => {
            return page_current !== 0;
        },

        hasNext: () => {
            return page_count ? page_current !== page_count - 1 : true;
        },

        isLast: () => {
            return page_count ? page_current === page_count - 1 : false;
        },

        lastPage: page_count ? Math.max(0, page_count - 1) : undefined
    };
}

const getter = (
    table_action: TableAction,
    page_current: number,
    page_size: number,
    page_count: number | undefined,
    setProps: SetProps,
    data: Data
): IPaginator => {
    if (table_action === TableAction.Native) {
        page_count = lastPage(data, page_size);
    }

    if (page_count) {
        page_count = Math.max(page_count, 1);
    }

    return makePaginator(
        table_action === TableAction.None
            ? null
            : {
                  setProps,
                  page_current,
                  page_count
              }
    );
};

export default memoizeOneFactory(getter);
