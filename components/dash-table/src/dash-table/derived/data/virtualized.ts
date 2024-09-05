import * as R from 'ramda';

import {memoizeOneFactory} from 'core/memoizer';
import {
    IDerivedData,
    IUserInterfaceViewport,
    IUserInterfaceCell,
    IVirtualizedDerivedData
} from 'dash-table/components/Table/props';

const getter = (
    virtualization: boolean,
    uiCell: IUserInterfaceCell | undefined,
    uiHeaders: IUserInterfaceCell[] | undefined,
    uiViewport: IUserInterfaceViewport | undefined,
    viewport: IDerivedData
): IVirtualizedDerivedData => {
    if (!virtualization) {
        return {
            ...viewport,
            offset: {rows: 0, columns: 0},
            padding: {
                rows: {before: 0, after: 0}
            }
        };
    }

    if (!uiViewport || !uiCell) {
        return {
            data: viewport.data.slice(0, 1),
            indices: viewport.indices.slice(0, 1),
            offset: {rows: 0, columns: 0},
            padding: {
                rows: {before: 0, after: 0}
            }
        };
    }

    const headersHeight = R.sum(R.map(h => h.height, uiHeaders || []));

    const scrollTop = Math.max(uiViewport.scrollTop - headersHeight, 0);
    const headersVisible = Math.max(headersHeight - uiViewport.scrollTop, 0);

    let start = Math.floor(scrollTop / uiCell.height);
    let end = Math.ceil(
        (uiViewport.height - headersVisible + scrollTop) / uiCell.height
    );

    const before = Math.min(start, 1);
    const after = Math.min(viewport.data.length - end, 1);

    start -= before;
    end += after;

    return {
        data: viewport.data.slice(start, end),
        indices: viewport.indices.slice(start, end),
        offset: {rows: start, columns: 0},
        padding: {
            rows: {before, after}
        }
    };
};

export default memoizeOneFactory(getter);
